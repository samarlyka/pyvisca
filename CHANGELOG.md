# pyvisca CHANGELOG

## v0.1.6

- Fix: Removed obsolete `scipy` dependency

## v0.1.5

- New: Ability to get power/stand-by state
- New: Added the ability to reload the current PTZ camera's serial port
- Fix: "self" not found when calling Camera.close()

## v0.1.4

- Fixed: Write timeout exception during program execution

## v0.1.3
- Fixed: When the relative zoom value is lower than 0, the camera zooms out instead

## v0.1.2
- New: Ability to get the current absolute zoom value
- New: Ability to set absolute and relative zoom values

## v0.1.1

- New: Ability to get the current absolute pan and tilt values
- New: Ability to set absolute and relative pan and tilt values

## v0.0.5

- Fixed: TypeError when trying to read input package from PTZ
- New: (Backend) Ability to send inquiry and directly receive input package

## v0.0.4

- New: Manual adjustment of camera's gain control
- New: Freezing the camera view

## v0.0.3

- Fixed: Cannot close port when opened
- New: Manual setting of camera focus
- New: Manual adjustment of camera aperture
- New: Toggling on/off of backlight compensation

## v0.0.2

- Info: Converted from Python 2.0 to Python 3.0
- New: Ability to zoom in/out the camera
- New: Ability to set and recall presets
- New: Ability to turn the PTZ camera on and off
- New: Ability to change iris setting
- New: Ability to change brightness setting

## v0.0.1

- Info: Initial forking of the repository from the work by Matthew Mage
- New: Panning the camera left, up, right, and down
- New: Homing the camera position to its default position
- New: Enabling autofocus of camera lens
- New: Setting picture effect (on supported devices only)
- New: Setting white balance
- New: Move relative to the current position
