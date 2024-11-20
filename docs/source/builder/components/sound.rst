.. _sound:

Sound Component
-------------------------------

Parameters
~~~~~~~~~~~~

name : string
    Everything in a |PsychoPy| experiment needs a unique name. The name should contain only letters, numbers and underscores (no punctuation marks or spaces).
    
start : float or integer
    The time that the stimulus should first play. See :ref:`startStop` for details.

stop : 
    For sounds loaded from a file leave this blank and then give the `Expected duration` below for 
    visualisation purposes. See :ref:`startStop` for details.
    
sound : 
    This sound can be described in a variety of ways:
      
      * a number can specify the frequency in Hz (e.g. 440)
      * a letter gives a note name (e.g. "C") and sharp or flat can also be added (e.g. "Csh" "Bf")
      * a filename, which can be a relative or absolute path (mid, wav, and ogg are supported).

Playback
========
How should stimulus play? Speed, volume, etc.

volume : float or integer
    The volume with which the sound should be played. It's a normalized value between 0 (minimum) 
    and 1 (maximum).

hamming window : bool
    For tones we can apply a hamming window to prevent 'clicks' that are caused by a sudden onset. 
    This delays onset by roughly 1ms.

Stop with Routine? : bool
    Should playback cease when the Routine ends? Untick to continue playing after the Routine has 
    finished.

Force end of Routine : bool
    Should the end of the sound cause the end of the Routine (e.g. trial)?

Device
========
Parameters for setting up the :class:`~psychopy.hardware.speaker.SpeakerDevice` which this sound will play on.

Speaker : str
    Choose from a dropdown list of available speaker devices which one to use.

Resampling : str
    If the given sound is a different sample rate from the given speaker, when should resampling 
    happen? Options are:
    * On load: Let PsychoPy resample audio clips when they're loaded. This allows low latency on 
      playback, but can mean slower loading with large files. This is the default mode.
    * When playing: Let your operating system handle resampling on playback. Not recommended for low 
      latency playback.
    * Do not resample: Do not resample audio clips. This is the safest option for low latency and fast 
      loading but means you'll get errors playing audio clips with a different sample rate to the 
      speaker / to previously played audio clips. Approach with caution.

Exclusive control : bool
    Should PsychoPy take exclusive control of the speaker, denying other applications access 
    when in use? In most cases the answer is no, but if you're not resampling then taking 
    exclusive control allows you to play audio clips of a different sample rate to the speaker 
    without having to resample them (provided they are the same sample rate as one another).


.. seealso::
	
	API reference for :class:`~psychopy.sound.SoundPyo`
