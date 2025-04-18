#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2025 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
import subprocess
import re
import time, sys, os
import argparse
import shutil
import argparse
import functools

unbuffered_print = functools.partial(print, flush=True)

thisFolder = Path(__file__).parent
finalDistFolder = thisFolder.parent.parent/'dist'

ENTITLEMENTS = (thisFolder / "entitlements.plist").absolute()
assert ENTITLEMENTS.exists()
BUNDLE_ID = "org.opensciencetools.psychopy"
USERNAME = "admin@opensciencetools.org"

SIGN_ALL = True
logFile = open("_lastCodeSign.log", "w")

# handy resources for info:
#
# to get a new Apple app-specific password:
#   https://appleid.apple.com/account/manage NOT developer.apple.com
# why use zip file to notarize as well as dmg:
#   https://deciphertools.com/blog/notarizing-dmg/
# notarize from Python:
#   https://github.com/najiji/notarizer/blob/master/notarize.py
# apple entitlements:
#     https://developer.apple.com/documentation/xcode/notarizing_macos_software_before_distribution/resolving_common_notarization_issues


class AppSigner:
    def __init__(self, appFile, version, destination=None, verbose=False,
                 team_id='', apple_id='', pword=''):
        self.appFile = Path(appFile)
        self.version = version
        self.destination = destination
        self._zipFile = None #'/Users/lpzjwp/code/psychopy/git/dist/PsychoPy3_2020.2.3.zip'
        self._appNotarizeUUID = None
        self._dmgBuildFile = None
        self._pword = pword
        self.verbose = verbose
        self._apple_id = apple_id
        self._team_id = team_id

    def signAll(self, verbose=None):
        if verbose is None:
            verbose = self.verbose
        # remove files that we know will fail the signing:
        for filename in self.appFile.glob("**/Frameworks/SDL*"):
            shutil.rmtree(filename)
        for filename in self.appFile.glob("**/Frameworks/eyelink*"):
            shutil.rmtree(filename)

        # this never really worked - probably the files signed in wrong order?
        # find all the included dylibs
        unbuffered_print('Signing dylibs:', end='')
        files = list(self.appFile.glob('**/*.dylib'))
        files.extend(self.appFile.glob('**/*.so'))
        files.extend(self.appFile.glob('**/git-core/git*'))
        files.extend(self.appFile.glob('**/git-core/scalar'))  # for some reason it's named differently
        files.extend(self.appFile.glob('**/cv2/.dylibs/*'))
        # ffmpeg
        files.extend(self.appFile.glob('**/imageio_ffmpeg/binaries/*'))
        files.extend(self.appFile.glob('**/resources/ffmpeg/ffmpeg-osx*'))
        # PyQt
        files.extend(self.appFile.glob('**/Versions/5/Qt*'))  # PyQt5
        files.extend(self.appFile.glob('**/Versions/A/Qt*'))  # PyQt6
        files.extend(self.appFile.glob('**/Contents/MacOS/QtWebEngineProcess'))
        files.extend(self.appFile.glob('**/Resources/lib/python3.8/lib-dynload/*.so'))
        files.extend(self.appFile.glob('**/Frameworks/Python.framework'))
        files.extend(self.appFile.glob('**/Contents/MacOS/python'))

        # ready? Let's do this!
        t0 = time.time()
        unbuffered_print(f"Signing dylibs...see {logFile.name} for details. key: \n"
              " . success\n"
              " o already signed\n"
              " - failed (deleted)\n"
              " X failed (couldn't delete)")
        for filename in files:
            if filename.exists():  # might have been removed since glob
                self.signSingleFile(filename, verbose=False, removeFailed=True)
        unbuffered_print(f'\n...done signing dylibs in {time.time()-t0:.03f}s')

        # then sign the outer app file
        unbuffered_print('Signing app')
        t0 = time.time()
        self.signSingleFile(self.appFile, removeFailed=False)
        unbuffered_print(f'...done signing app in {time.time()-t0:.03f}s')

    def signSingleFile(self, filename, removeFailed=False, verbose=None):
        """Signs a single file (if it isn't already signed)

        Returns:
            True (success)
            list of warnings (partial success)
            False (failed)
        Params:
            filename
            removedFailed (bool): if True then try to remove files that don't sign
            verbose: increases printing level (although you can see the logs)
        """

        # " . success\n"
        # " - failed (deleted)\n"
        # " X failed (couldn't delete)

        if verbose is None:
            verbose = self.verbose

        # is there already a valid signature? MUST overwrite or won't notarize
        # if self.signCheck(str(filename)) is True:  # check actual boolean, not list of warnings
        #     unbuffered_print('o', end='')
        #     return True

        # try signing it ourselves
        if not self._apple_id:
            raise ValueError('No identity provided for signing')
        cmd = ['codesign', str(filename),
               '--sign', self._team_id,
               '--entitlements', str(ENTITLEMENTS),
               '--force',
               '--timestamp',
               # '--deep',  # not recommended although used in most demos
               '--options', 'runtime',
               ]
        cmdStr = ' '.join(cmd)
        logFile.write(f"{cmdStr}\n")
        if verbose:
            unbuffered_print(cmdStr)
        exitcode, output = subprocess.getstatusoutput(cmdStr)
        if verbose and output:
            unbuffered_print(output)


        # CODESIGN SUCCESS
        if exitcode == 0 and not ('failed' in output):
            # successfully signed
            unbuffered_print('.', end='')
            # do a detailed check and return
            return self.signCheck(filename, verbose=False, removeFailed=removeFailed)
        
        # CODESIGN FAIL. Let's see if we can remove
        logFile.write(f"{output}\n")
        try: # remove the file because we couldn't sign it
            Path(filename).unlink()
            unbuffered_print('-', end='')
            logFile.write(f"FILE {filename}: failed to codesign and was removed\n")
        except:
            unbuffered_print('X', end='')
            logFile.write(f"\nFILE {filename}: failed to codesign and failed to remove\n")
        return 

    def signCheck(self, filepath=None, verbose=False, strict=True,
                  removeFailed=False):
        """Checks whether a file is signed and returns a list of warnings
        Returns:
            False if not signed at all
            A list of warnings if signed but with concerns (and these are printed)
            True if signed with no warnings found
            """
        if not filepath:
            filepath = self.appFile
        # just check the details
        strictFlag = "--strict" if strict else ""
        cmdStr = f'codesign -dvvv {strictFlag} {filepath}'
        # make the call
        if verbose:
            unbuffered_print(cmdStr)
        exitcode, output = subprocess.getstatusoutput(cmdStr)
        if verbose:
            unbuffered_print(f"Checking that codesign worked: {output}")
        
        if exitcode == 1: # indicates no valid signature
            return False  

        # check for warnings
        warnings=[]
        for line in output.split("\n"):
            if 'warning' in line.lower():
                warnings.append(line)
        if warnings:
            unbuffered_print(filepath)
            for line in warnings:
                unbuffered_print("  ", line)
            if removeFailed:
                Path(filepath).unlink()
                unbuffered_print(f"REMOVED FILE {filepath}: failed to codesign")
            return warnings
        else:
            return True

    def upload(self, fileToNotarize):
        """Uploads a file to Apple for notarizing"""
        if not self._pword:
            raise ValueError('No app-specific password provided for notarizing')
        filename = Path(fileToNotarize).name
        unbuffered_print(f'Sending {filename} to apple for notarizing')
        cmdStr = (f'xcrun notarytool submit {fileToNotarize} '
                  f'--apple-id "{self._apple_id}" '
                  f'--team-id "{self._team_id}" '
                  f'--password "{self._pword}"')
        # cmdStr = (f"xcrun altool --notarize-app -t osx -f {fileToNotarize} "
        #           f"--primary-bundle-id {BUNDLE_ID} -u {USERNAME} ")
        # unbuffered_print(cmdStr)
        t0 = time.time()
        exitcode, output = subprocess.getstatusoutput(cmdStr)
        m = re.findall(r"^  id: (.*)$", output, re.M)

        if 'Please sign in with an app-specific password' in output:
            unbuffered_print("[Error] Upload failed: You probably need a new app-specific "
                  "password from https://appleid.apple.com/account/manage")
            exit(1)
        elif exitcode != 0:
            unbuffered_print(f"[Error] Upload failed with message: {output}")
            exit(exitcode)

        unbuffered_print(output)
        uuid = m[0].strip()
        self._appNotarizeUUID = uuid
        unbuffered_print(f'Uploaded file {filename} in {time.time()-t0:.03f}s: {uuid}')
        unbuffered_print(f'Upload to Apple completed at {time.ctime()}')
        return uuid

    @property
    def dmgFile(self):
        if not self._dmgBuildFile:
            self._dmgBuildFile = self._buildDMG()
        return self._dmgBuildFile

    @property
    def zipFile(self):
        if self._zipFile:
            return self._zipFile
        else:
            unbuffered_print("Creating zip archive to send to Apple: ", end='')
            zipFilename = self.appFile.parent / (self.appFile.stem+f'_{self.version}.zip')
            shutil.rmtree(zipFilename, ignore_errors=True)
            # zipFilename.unlink(missing_ok=True)  # remove the file if it exists
            t0 = time.time()
            cmdStr = f'/usr/bin/ditto -c -k --keepParent {self.appFile} {zipFilename}'
            unbuffered_print(cmdStr)
            exitcode, output = subprocess.getstatusoutput(cmdStr)
            if exitcode == 0:
                unbuffered_print(f"Done creating zip in {time.time()-t0:.03f}s")
            else:
                unbuffered_print(output)
            self._zipFile = zipFilename
            return zipFilename

    def awaitNotarized(self, logFile='_notarization.json'):
        unbuffered_print("Waiting for notarization to complete"); sys.stdout.flush()
        # can use 'xcrun notarytool info' to check status or 'xcrun notarytool wait'
        exitcode, output = subprocess.getstatusoutput(f'xcrun notarytool wait {self._appNotarizeUUID} '
                  f'--apple-id "{self._apple_id}" '
                  f'--team-id {self._team_id} '
                  f'--password {self._pword}')
        unbuffered_print(output); sys.stdout.flush()
        unbuffered_print("Fetching notarisation log"); sys.stdout.flush()
        # always fetch the log file too
        exitcode2, output = subprocess.getstatusoutput(f'xcrun notarytool log {self._appNotarizeUUID} '
                  f'--apple-id "{self._apple_id}" '
                  f'--team-id {self._team_id} '
                  f'--password {self._pword} '
                  f'{logFile}')
        unbuffered_print(output)
        if exitcode != 0:
            unbuffered_print("`xcrun notarytool wait` returned exit code {exitcode}. Exiting immediately.")
            exit(exitcode)


    def staple(self, filepath):
        cmdStr = f'xcrun stapler staple {filepath}'; sys.stdout.flush()
        unbuffered_print(cmdStr)
        exitcode, output = subprocess.getstatusoutput(cmdStr)
        unbuffered_print(f"exitcode={exitcode}: {output}"); sys.stdout.flush()
        if exitcode != 0:
            unbuffered_print('*********Staple failed*************')
            exit(exitcode)
        else:
            unbuffered_print(f"Staple successful. You can verify with\n    xcrun stapler validate {filepath}"); sys.stdout.flush()

    def dmgBuild(self):
        import dmgbuild
        dmgFilename = str(self.appFile).replace(".app", "_rw.dmg")
        appName = self.appFile.name
        unbuffered_print(f"building dmg file: {dmgFilename}..."); sys.stdout.flush()
        # remove previous file if it's there
        if Path(dmgFilename).exists():
            os.remove(dmgFilename)
        # then build new one

        icon = (thisFolder.parent /
                'psychopy/app/Resources/psychopy.icns').resolve()
        background = (thisFolder / "dmg722x241.tiff").resolve()
        dmgbuild.build_dmg(
                filename=dmgFilename,
                volume_name=f'PsychoPy-{self.version}',  # avoid spaces
                settings={
                    'format': 'UDRW',
                    'files': [str(self.appFile)],
                    'symlinks': { 'Applications': '/Applications' },
                    'size': '3g',  # but maybe irrelevant in UDRW mode?
                    'badge_icon': str(icon),
                    'background': None,  # background
                    'icon_size': 128,
                    'icon_locations': {
                        'PsychoPy.app': (150, 160),
                        'Applications': (350, 160)
                    },
                    'window_rect': ((600, 600), (500, 400)),
                },
        )
        unbuffered_print(f"building dmg file complete")
        return dmgFilename

    def dmgStapleInside(self):
        dmgFilename = str(self.appFile).replace(".app", "_rw.dmg")
        appName = self.appFile.name
        """Staple the notarization to the app inside the r/w dmg file"""
        # staple the file inside the dmg
        cmdStr = f"hdiutil attach '{dmgFilename}'"
        exitcode, output = subprocess.getstatusoutput(cmdStr)
        # subprocess.getstatusoutput("say 'waiting' --voice=Kate")
        time.sleep(10)
        volName = output.split('\t')[-1]
        self.staple(f"'{volName}/{appName}'")
    
        time.sleep(10)  # wait for 10s and then try more forcefully

        # try to eject all volumens with PsychoPy in the name
        for volume in Path("/Volumes").glob("PsychoPy*"):
            # Eject the disk image
            for attemptN in range(5):
                exitcode, output = subprocess.getstatusoutput(f"diskutil eject {volume}")
                unbuffered_print(f"Attempt {attemptN}: {output}"); sys.stdout.flush()
                if exitcode == 0:
                    break
                # have a rest and try again
                time.sleep(5)

    def dmgCompress(self):
        dmgFilename = str(self.appFile).replace(".app", "_rw.dmg")
        dmgFinalFilename = self.appFile.parent / f"StandalonePsychoPy-{self.version}-macOS.dmg"
        # remove previous file if it's there
        if Path(dmgFinalFilename).exists():
            os.remove(dmgFinalFilename)

        cmdStr = f"hdiutil convert {dmgFilename} -format UDZO -o {dmgFinalFilename}"
        for attemptN in range(5):
            unbuffered_print(f"Attempt {attemptN}: {cmdStr}")
            exitcode, output = subprocess.getstatusoutput(cmdStr)
            unbuffered_print(output)
            if exitcode == 0:
                return dmgFinalFilename
        
        raise RuntimeError(f'****Failed to compress {dmgFilename} to {dmgFinalFilename} (is it not ejected?) ****')


def main():

    with open(thisFolder.parent / "psychopy/VERSION") as f:
        defaultVersion = f.read().strip()
    parser = argparse.ArgumentParser(description="Codesigning PsychoPy.app")
    parser.add_argument("--app", help=("Path to the app bundle, "
                                       "assumed to be in dist/"),
                        action='store', required=False, default="PsychoPy.app")
    parser.add_argument("--version", help="Version of the app",
                        action='store', required=False, default=defaultVersion)
    parser.add_argument("--file", help="path for a single file to be signed",
                        action='store', required=False, default=None)
    parser.add_argument("--skipNotarize", help="Include this flag only if you want to skip",
                        action='store', required=False, default=None)
    parser.add_argument("--runPreDmgBuild", help="Runs up until dmg is built (and notarized) then exits",
                        action='store', required=False, default='true')
    parser.add_argument("--runDmgBuild", help="Runs the dmg build itself",
                        action='store', required=False, default='true')
    parser.add_argument("--runPostDmgBuild", help="Runs up until dmg is built (and notarized) then exits",
                        action='store', required=False, default='true')
    parser.add_argument("--teamId", help="ost id from apple for codesigning",
                        action='store', required=False, default=None)
    parser.add_argument("--appleId", help="apple id for codesigning",
                        action='store', required=False, default=None)
    parser.add_argument("--pwd", help="password for app-specific password",
                        action='store', required=False, default=None)
    args = parser.parse_args()
    args.runPreDmgBuild = args.runPreDmgBuild.lower() in ['true', 'True', '1', 'y', 'yes']
    args.runDmgBuild = args.runDmgBuild.lower() in ['true', 'True', '1', 'y', 'yes']
    args.runPostDmgBuild = args.runPostDmgBuild.lower() in ['true', 'True', '1', 'y', 'yes']

    if args.skipNotarize in ['true', 'True', '1', 'y', 'yes']:
        NOTARIZE = False
    else:
        NOTARIZE = True

    # codesigning TEAM_ID from CLI args?
    if args.teamId:
        TEAM_ID = args.teamId
    else:
        with Path().home()/ 'keys/apple_ost_id' as p:
            TEAM_ID = p.read_text().strip()
    if args.appleId:
        APPLE_ID = args.appleId
    else:
        with Path().home()/ 'keys/apple_id' as p:
            APPLE_ID = p.read_text().strip()
    if args.pwd:
        PWORD = args.pwd
    else:
        with Path().home()/ 'keys/apple_psychopy_app_specific' as p:
            PWORD = p.read_text().strip()
            
    if args.file:  # not the whole app - just sign one file
        distFolder = (thisFolder / '../dist').resolve()
        signer = AppSigner(appFile='', version=None, 
                           pword=PWORD, team_id=TEAM_ID, apple_id=APPLE_ID)
        signer.signSingleFile(args.file, removeFailed=False, verbose=True)
        signer.signCheck(args.file, verbose=True)

        if NOTARIZE:
            signer.upload(args.file)
            # notarize and staple
            signer.awaitNotarized()
            signer.staple(args.file)

    else:  # full app signing and notarization
        distFolder = (thisFolder / '../dist').resolve()
        signer = AppSigner(appFile=distFolder/args.app, version=args.version, 
                           pword=PWORD, team_id=TEAM_ID, apple_id=APPLE_ID)

        if args.runPreDmgBuild:
            if SIGN_ALL:
                signer.signAll()
            signer.signCheck(verbose=False)

        if args.runDmgBuild:
            if NOTARIZE:
                unbuffered_print(f'Signer.upload("{signer.zipFile}")'); sys.stdout.flush()
                signer.upload(signer.zipFile)
            # build the read/writable dmg file (while waiting for notarize)
            signer.dmgBuild()
            if NOTARIZE:
                # notarize and staple
                unbuffered_print(f'Signer.awaitNotarized()'); sys.stdout.flush()
                signer.awaitNotarized()

        if args.runPostDmgBuild:
            unbuffered_print(f'Signer.dmgStapleInside()'); sys.stdout.flush()
            signer.dmgStapleInside()  # doesn't require UUID
            unbuffered_print(f'Signer.dmgCompress()'); sys.stdout.flush()
            dmgFile = signer.dmgCompress()
            unbuffered_print(f'Signer.signSingleFile(dmgFile'); sys.stdout.flush()
            signer.signSingleFile(dmgFile, removeFailed=False, verbose=True)

            if NOTARIZE:
                unbuffered_print(f'Signer.upload(dmgFile)'); sys.stdout.flush()
                OK = signer.upload(dmgFile)
                if not OK: 
                    return 0
                # notarize and staple
                unbuffered_print(f'Signer.awaitNotarized()'); sys.stdout.flush()
                signer.awaitNotarized(logFile="")  # don't need the log file for the dmg
                unbuffered_print(f'Signer.staple(dmgFile)'); sys.stdout.flush()
                signer.staple(dmgFile)


if __name__ == "__main__":
    main()
