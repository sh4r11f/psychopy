:orphan:

.. _components:


------------------------------------------
Components
------------------------------------------

The following Components are available from Builder:

.. toctree::
   :maxdepth: 1   
   :glob:

   *

About Components
------------------------------------------

Routines in the Builder contain any number of components, which typically define the parameters of a stimulus or an input/output device.

.. _entering-params:

Entering parameters
==========================================

Most of the entry boxes for Component parameters simply receive text or numeric values or lists (sequences of values surrounded by square brackets) as input. In addition, the user can insert variables and code into most of these, which will be interpreted either at the beginning of the experiment or at regular intervals within it.

To indicate to |PsychoPy| that the value represents a variable or python code, rather than literal text, it should be preceded by a `$`. For example, inserting `intensity` into the text field of the Text Component will cause that word literally to be presented, whereas `$intensity` will cause python to search for the variable called intensity in the script.

Variables associated with :ref:`loops` can also be entered in this way (see :ref:`"Using loops to update stimuli trial-by-trial"<accessing-params>` for further details). But it can also be used to evaluate arbitrary python code. 

For example:

* :code:`$random(2)` will generate a pair of random numbers
* :code:`$"yn"[randint(2)]` will randomly choose the first or second character (y or n)
* :code:`$globalClock.getTime()` will insert the current time in secs of the globalClock object
* :code:`$[sin(angle), cos(angle)]` will insert the sin and cos of an angle (e.g. into the x,y coords of a stimulus)


How often to evaluate the variable/code
==========================================

If you do want the parameters of a stimulus to be evaluated by code in this way you need also to decide how often it should be updated. By default, the parameters of Components are set to be `constant`; the parameter will be set at the beginning of the experiment and will remain that way for the duration. Alternatively, they can be set to change either on `every repeat` in which case the parameter will be set at the beginning of the Routine on each repeat of it. Lastly many parameters can even be set `on every frame`, allowing them to change constantly on every refresh of the screen.

.. _Python: http://www.python.org
.. _numpy.random.rand(): http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.rand.html#numpy.random.rand
.. _numpy: http://numpy.scipy.org/

.. redirect::
   reward.rst > https://github.com/psychopy/psychopy-labeotech
   ratingscale.rst > https://psychopy.github.io/psychopy-legacy/builder/components/RatingScaleComponent/
   pump.rst > https://github.com/psychopy/psychopy-qmix
   patch.rst > https://psychopy.github.io/psychopy-legacy/builder/components/PatchComponent/
   ioLabs.rst > https://psychopy.github.io/psychopy-iolabs/builder/components/IoLabsButtonBox/
   emotiv_record.rst > https://psychopy.github.io/psychopy-emotiv/emotiv_record.html
   emotiv_marking.rst > https://psychopy.github.io/psychopy-emotiv/emotiv_marking.html
   cedrusResponseBox.rst > https://psychopy.github.io/psychopy-cedrus/builder/components/CedrusButtonBoxComponent/
   