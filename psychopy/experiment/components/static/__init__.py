#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Part of the PsychoPy library
Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2025 Open Science Tools Ltd.
Distributed under the terms of the GNU General Public License (GPL).
"""

from pathlib import Path
from psychopy.experiment.components import BaseComponent, Param, _translate

__author__ = 'Jon Peirce'


class StaticComponent(BaseComponent):
    """A Static Component, allowing frame rendering to pause.

    E.g., pause while disk is accessed for loading an image
    """
    # override the categories property below
    # an attribute of the class, determines the section in the components panel
    categories = ['Custom']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'static.png'
    tooltip = _translate('Static: Static screen period (e.g. an ISI). '
                         'Useful for pre-loading stimuli.')

    def __init__(
            self, exp, parentName, 
            # basic
            name='ISI',
            startType='time (s)', startVal=0.0,
            stopType='duration (s)', stopVal=0.5,
            startEstim='', durationEstim='',
            # custom
            code="",
            # data
            saveData=False
        ):
        BaseComponent.__init__(
            self, exp, parentName, name=name,
            startType=startType, startVal=startVal,
            stopType=stopType, stopVal=stopVal,
            startEstim=startEstim, durationEstim=durationEstim
        )
        self.updatesList = []  # a list of dicts {compParams, fieldName}
        self.type = 'Static'
        self.url = "https://www.psychopy.org/builder/components/static.html"
        # --- Custom params ---
        self.order += [
            "code",
            "saveData",
        ]
        self.params['code'] = Param(
            code, valType='code', inputType="multi", categ='Custom',
            label=_translate("Custom code"),
            hint=_translate(
                "Custom code to be run during the static period (after updates)"
            )
        )
        self.params['saveData'] = Param(
            saveData, valType="code", inputType="bool", categ="Custom",
            label=_translate("Save data during"),
            hint=_translate(
                "While the frame loop is paused, should we take the opportunity to save data now? "
                "This is only relevant locally, online data saving is either periodic or on close."
            )
        )

    def addComponentUpdate(self, routine, compName, fieldName):
        self.updatesList.append({'compName': compName,
                                 'fieldName': fieldName,
                                 'routine': routine})

    def remComponentUpdate(self, routine, compName, fieldName):
        # have to do this in a loop rather than a simple remove
        target = {'compName': compName, 'fieldName': fieldName,
                  'routine': routine}

        for item in self.updatesList:
            # check if dict has the same fields
            for key in ('compName', 'fieldName', 'routine'):
                if item[key] != target[key]:
                    break
            else:
                self.updatesList.remove(item)

            # NB - should we break out of it here if an item is found?

    def writeInitCode(self, buff):
        code = ("%(name)s = clock.StaticPeriod(win=win, "
                "screenHz=expInfo['frameRate'], name='%(name)s')\n")
        buff.writeIndented(code % self.params)

    def writeInitCodeJS(self, buff):
        code = (
            "%(name)s = new core.MinimalStim({\n"
        )
        buff.writeIndentedLines(code % self.params)

        buff.setIndentLevel(+1, relative=True)
        code = (
                "name: \"%(name)s\", \n"
                "win: psychoJS.window,\n"
                "autoDraw: false, \n"
                "autoLog: true, \n"
        )
        buff.writeIndentedLines(code % self.params)

        buff.setIndentLevel(-1, relative=True)
        code = (
            "});\n"
        )
        buff.writeIndented(code % self.params)

    def writeFrameCode(self, buff):
        if self.writeStartTestCode(buff):
            buff.setIndentLevel(-1, relative=True)
        self.writeStopTestCode(buff)

    def writeFrameCodeJS(self, buff):
        # Start test
        indent = self.writeStartTestCodeJS(buff)
        if indent:
            buff.writeIndentedLines("%(name)s.status = PsychoJS.Status.STARTED;\n" % self.params)
            self.writeParamUpdates(buff, target="PsychoJS")
            buff.setIndentLevel(-indent, relative=True)
            buff.writeIndentedLines("}")

        # Stop test, with stop actions
        indent = self.writeStopTestCodeJS(buff)
        if indent:
            for update in self.updatesList:

                # Get params for update
                compName = update['compName']
                fieldName = update['fieldName']
                # routine = self.exp.routines[update['routine']]
                if hasattr(compName, 'params'):
                    prms = compName.params  # it's already a compon so get params
                else:
                    # it's a name so get compon and then get params
                    prms = self.exp.getComponentFromName(str(compName)).params
                if prms[fieldName].valType == "file":
                    # Check resource manager status
                    code = (
                        f"if (psychoJS.serverManager.getResourceStatus({prms[fieldName]}) === core.ServerManager.ResourceStatus.DOWNLOADED) {{\n"
                    )
                    buff.writeIndentedLines(code % self.params)
                    # Print confirmation
                    buff.setIndentLevel(+1, relative=True)
                    code = (
                        "console.log('finished downloading resources specified by component %(name)s');\n"
                    )
                    buff.writeIndentedLines(code % self.params)
                    # else...
                    buff.setIndentLevel(-1, relative=True)
                    code = (
                        "} else {\n"
                    )
                    buff.writeIndentedLines(code % self.params)
                    # Print warning if not downloaded
                    buff.setIndentLevel(+1, relative=True)
                    code = (
                        f"console.log('resource specified in %(name)s took longer than expected to download');\n"
                        f"await waitForResources(resources = {prms[fieldName]})"
                    )
                    buff.writeIndentedLines(code % self.params)
                    buff.setIndentLevel(-1, relative=True)
                    buff.writeIndentedLines("}\n")
            buff.writeIndentedLines("%(name)s.status = PsychoJS.Status.FINISHED;\n" % self.params)
            # Escape stop code indent
            buff.setIndentLevel(-indent, relative=True)
            buff.writeIndentedLines("}\n")

    def writeStartTestCode(self, buff):
        """This will be executed as the final component in the routine
        """
        buff.writeIndented("# *%s* period\n" % (self.params['name']))
        needsUnindent = BaseComponent.writeStartTestCode(self, buff)
        if needsUnindent:
            if self.params['stopVal'] in ("", "-1", "None", None):
                # if duration is infinite, set it to extremely long and warn the user
                durationSecsStr = "FOREVER"
            elif self.params['stopType'].val == 'time (s)':
                durationSecsStr = "%(stopVal)s-t" % (self.params)
            elif self.params['stopType'].val == 'duration (s)':
                durationSecsStr = "%(stopVal)s" % (self.params)
            elif self.params['stopType'].val == 'duration (frames)':
                durationSecsStr = "%(stopVal)s*frameDur" % (self.params)
            elif self.params['stopType'].val == 'frame N':
                durationSecsStr = "(%(stopVal)s-frameN)*frameDur" % (self.params)
            else:
                msg = ("Couldn't deduce end point for startType=%(startType)s, "
                       "stopType=%(stopType)s")
                raise Exception(msg % self.params)
            # save data
            if self.params['saveData']:
                code = (
                    "# take the opportunity to save data file now (to be updated later)\n"
                    "_%(name)sLastFileNames = thisExp.save()\n"
                    "thisExp.queueNextCollision('overwrite', fileName=_%(name)sLastFileNames)\n"
                )
                buff.writeIndentedLines(code % self.params)
            # start static
            code = (
                "# start the static period\n"
                "%(name)s.start({})\n"
            ).format(durationSecsStr)
            buff.writeIndentedLines(code % self.params)
        
        return needsUnindent

    def writeStopTestCode(self, buff):
        """Test whether we need to stop
        """
        code = ("elif %(name)s.status == STARTED:  # one frame should "
                "pass before updating params and completing\n")
        buff.writeIndented(code % self.params)
        buff.setIndentLevel(+1, relative=True)  # entered an if statement
        self.writeParamUpdates(buff)
        # finish
        code = (
            "# finish the static period and store its duration\n"
            "%(name)s.complete()\n"
            "%(name)s.tStop = %(name)s.tStart + %(name)s.getDuration()\n"
        )
        buff.writeIndentedLines(code % self.params)
        # to get out of the if statement
        buff.setIndentLevel(-1, relative=True)

    def writeParamUpdates(self, buff, updateType=None, paramNames=None, target="PsychoPy"):
        """Write updates. Unlike most components, which us this method
        to update themselves, the Static Component uses this to update
        *other* components
        """
        if updateType == 'set every repeat':
            return  # the static component doesn't need to change itself
        if len(self.updatesList):
            # Comment to mark start of updates
            if target == "PsychoJS":
                code = "// Updating other components during *%s*\n"
            else:
                code = "# Updating other components during *%s*\n"
            buff.writeIndented(code % self.params['name'])
            # Do updates
            for update in self.updatesList:
                compName = update['compName']
                fieldName = update['fieldName']
                # get component
                if hasattr(compName, 'params'):
                    comp = compName
                else:
                    comp = self.exp.getComponentFromName(str(compName))
                # component may be disabled or otherwise not present - skip it if so
                if comp is None:
                    return
                # get params
                prms = comp.params  # it's already a compon so get params
                # If in JS, prepare resources
                if target == "PsychoJS" and prms[fieldName].valType == "file":
                    # Do resource manager stuff
                    code = (
                        f"console.log('register and start downloading resources specified by component %(name)s');\n"
                        f"await psychoJS.serverManager.prepareResources(%({fieldName})s);\n"
                        f"{self.params['name']}.status = PsychoJS.Status.STARTED;\n"
                    )
                    buff.writeIndentedLines(code % prms)
                # Set values
                self.writeParamUpdate(buff, compName=compName,
                                      paramName=fieldName,
                                      val=prms[fieldName],
                                      updateType=prms[fieldName].updates,
                                      params=prms, target=target)
            # Comment to mark end of updates
            if target == "PsychoJS":
                code = "// Component updates done\n"
            else:
                code = "# Component updates done\n"
            buff.writeIndentedLines(code)

            # Write custom code
            if self.params['code']:
                # Comment to mark start of custom code
                if target == "PsychoJS":
                    code = "// Adding custom code for %(name)s\n"
                else:
                    code = "# Adding custom code for %(name)s\n"
                buff.writeIndentedLines(code % self.params)
                # Write custom code
                code = "%(code)s\n"
                buff.writeIndentedLines(code % self.params)
