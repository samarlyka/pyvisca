# pyvisca

A Python module for controlling PTZ cameras running on Sony VISCA protocol via serial USB.

This repository is a "fork" of a previous Python VISCA library initially published on November 23, 2015 by **Matthew Mage** under the repo name [`python-visca`](https://github.com/Sciguymjm/python-visca) (GPL-3.0-licensed). The original code was written in Python 2.0, but was discontinued since 2016.

In **pyvisca**, we have converted the source code to make it compatible with Python 3.0. (Python 2.0 is [deprecated](https://www.python.org/doc/sunset-python-2), and the third version is used in most circumstances nowadays.) More functionalities and commands are also added to the library, which was previously unavailable in the original work done by Matthew Mage. These new commands include the following:

- Ability to zoom in/out the camera
- Ability to set and recall presets
- Ability to turn the PTZ camera on and off
- Ability to change iris setting
- Ability to change brightness setting
- Manually changing the camera focus
- Adjusting the camera's aperture value
- Adjusting the camera's gain value
- Turning on/off backlight compensation (on supported devices)
- Freezing the current camera view

The following commands were already present in the original work by Matthew Mage:

- Panning the camera left, up, right, and down
- Homing the camera position to its default position
- Enabling autofocus of camera lens
- Setting picture effect (on supported devices only)
- Setting white balance
- Moving the camera pan/tilt relative to the current position

Note that not every command can be executed in any given PTZ camera. Please refer to your VISCA-compatible PTZ camera's specification to see which commands and features are available.

## Installation

The **pyvisca** module can be installed directly from pip:

```bash
python -m pip install pyvisca
```

The Python script can also be downloaded directly from this repository and imported right away. To do so, run:

```bash
git clone https://github.com/samarlyka/pyvisca
```

Then `cd` into the `src` folder of the cloned repository, and execute the following line in the Python terminal:

```python
from pyvisca import visca
```

## Usage

The following is a basic example on how to make use of this library.

```python
from pyvisca import visca

# Instantiating a new VISCA PTZ object
# This also automatically initializes and connects to the serial port
cam = visca.PTZ('/dev/ttyUSB0')
# Windows users may need to run the following command instead
# cam = visca.PTZ('COM10')

# Turning the power of the camera on and off
# "1" for on, "0" for off (you can use "True" and "False" as well)
cam.power(1)

# Send the camera to its home/default position
cam.home()

# Move the camera in one direction
# This will send the camera to move indefinitely
cam.left()
cam.up()
cam.down()
cam.right(7)  # --- adjust movement speed by specifying 0-24; defaults to 5

# Move the camera in two directions
cam.left_up()
cam.left_down()
cam.right_up()
cam.right_down(3, 7)  # --- adjust movement speed by specifying 0-24 into (pan, tilt) parameter
                      # ---defaults to (5, 5)

# Relative movement
# ---
# relative_position(pan, tilt, amount_pan, amount_tilt, direction_pan, direction_tilt)
# 
# pan                       : pan speed (0-24)
# tilt                      : tilt speed (0-24)
# amount_pan, amount_tilt   : amount to move in pixels
# direction_pan             : 1 = right, -1 = left
# direction_tilt            : 1 = up,    -1 = down
cam.relative_position(2, 2, 100, 100, 1, -1)

# Stop the pan and/or tilt movements of the camera right away
cam.stop()

# Adjust camera zoom (wide or tele)
# This will send the camera to zoom indefinitely
cam.zoom_in()
cam.zoom_out(3)  # --- adjust zooming speed by specifying 0-7; defaults to 5

# Stop any zoom movement
cam.zoom_stop()

# Adjust the iris of the camera (constant speed)
cam.iris_up()
cam.iris_down()
cam.iris_reset()

# Adjust the brightness of the camera (constant speed)
cam.bright_up()
cam.bright_down()
cam.bright_reset()

# Assign the current camera position to a preset (0-255)
cam.preset_set(255)

# Recall a preset assignment (0-255)
cam.preset_recall(255)

# Setting white balance
cam.white_balance_auto()
cam.white_balance_indoor()
cam.white_balance_outdoor()

# Change picture effects
cam.picture_effect_b_w()
cam.picture_effect_mosaic()
cam.picture_effect_negative()
cam.picture_effect_pastel()
cam.picture_effect_sepia()
cam.picture_effect_slim()
cam.picture_effect_solarize()
cam.picture_effect_stretch()

# Turn off picture effect
cam.picture_effect_off()

# Turn on backlight compensation
# ("0" or "False" to turn off)
cam.backlight(1)

# Autofocus the camera
cam.autofocus()
cam.autofocus_sens_high()  # --- high sensitivity autofocus
cam.autofocus_sens_low()  # --- low sensitivity autofocus

# Manual focus of the camera
cam.focus_near()
cam.focus_far(3)  # --- adjust zooming speed by specifying 0-7; defaults to 5

# Stop any ongoing adjustment of camera focus
cam.focus_stop()

# Adjust the camera's aperture
cam.aperture_up()
cam.aperture_down()
cam.aperture_reset()

# Adjust the camera's gain
cam.gain_up()
cam.gain_down()
cam.gain_reset()

# Freeze the camera ("1" or "True")
cam.freeze(1)

# Unfreeze the camera ("0" or "False")
cam.freeze(0)
```

## Examples

More examples can be found in the repository's [example folder](https://github.com/samarlyka/pyvisca/tree/main/examples).

## Roadmap

In the future versions, we plan to add the following feature commands:

- ✔️ Adjust camera gain
- ✔️ Freeze the current view
- ✔️ Adjust camera aperture
- ✔️ Turn backlight compensation on/off (on supported devices)

## Contributing

If you find this library helpful, feel free to star [this repository](https://github.com/samarlyka/pyvisca).

You can also contribute by opening an issue, proposing a new feature, and creating a new pull request in this repository.

## Acknowledgement

The original work of this library is due to [Matthew Mage](https://github.com/Sciguymjm).

We refer to the following reference manual in developing this library: [https://docs.crestron.com/en-us/9326/Content/Topics/Configuration/VISCA-Comands.htm](https://docs.crestron.com/en-us/9326/Content/Topics/Configuration/VISCA-Comands.htm).
