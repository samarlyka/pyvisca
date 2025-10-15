# -*- coding: utf-8 -*-
# 
# The main script module file to control PTZ cameras based on VISCA serial protocol
# By Samarthya Lykamanuella
# Licensed under GPL-3.0
# ---
# Original work of this library is due to Matthew Mage
# -> SOURCE: https://github.com/Sciguymjm/python-visca
# VISCA command documentation was obtained from Crestron
# -> SOURCE: https://docs.crestron.com/en-us/9326/Content/Topics/Configuration/VISCA-Comands.htm

from time import sleep
import binascii
import re
import serial

class Camera(object):
    _input = None
    _input_string = None
    _output = None
    _output_string = None

    def __init__(self, output='COM10'):
        """General VISCA-based PTZ control class.
        
        Initializes camera object by connecting to serial port.
        :param output: Outbound serial port string. (default: 'COM10')
        :type output: str
        """
        self.serial_port = output
        
        # Setting "write_timeout" to zero prevents "write timeout exception".
        # SOURCE: https://stackoverflow.com/a/18314684
        self._output = serial.Serial(output, writeTimeout=0, write_timeout=0)
    
    def close(self):
        """Closes current serial port.

        :param serial_port: Serial port to modify.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if self._output.isOpen():
            self._output.close()
            return True
        else:
            print("Error closing serial port: Already closed.")
            return False
        
    def command(self, com):
        """Sends hexadecimal string to serial port.

        :param com: Command string. Hexadecimal format.
        :type com: str
        :return: Success.
        :rtype: bool
        """
        try:
            self._output.write(binascii.unhexlify(com))
            return True
        except Exception as e:
            print(com, e)
            return False
    
    def open(self, serial_port=''):
        """Opens serial port.

        :param serial_port: Serial port to modify.
        :return: True if successful, False if not.
        :rtype: bool
        """
        serial_port = self.serial_port if serial_port == '' else serial_port
        
        if not self._output.isOpen():
            self._output = serial.Serial(serial_port, writeTimeout=0, write_timeout=0)
            return True
        else:
            print("Error opening serial port: Already open.")
            return False
    
    def reset_port(self):
        """Resets the current port and reload that same port.
        This function attempts to close the serial port and re-open the same port.
        """
        # You must flush the buffer before closing, to avoid infinite closing hangs.
        # SOURCE: https://github.com/pyserial/pyserial/issues/226#issuecomment-520350383
        self._output.reset_input_buffer()
        
        # Reloading the port
        self._output.close()
        self._output.open()
        
    def read(self):
        """When receiving an input buffer, this function reads all pending input bytes.
        """
        msg = binascii.hexlify( self._output.read_all() )
        # Remove bothering "b" prefix
        msg = str(msg).replace('b\'', '').replace('\'', '')
        
        return msg
    
    def reset_input_buffer(self):
        """Reset the input buffer of the PTZ.
        """
        self._output.reset_input_buffer()

class PTZ(Camera):
    """Command class for general PTZ controller.
    
    In the original repo by Matthew Mage, it was initially
    developed for Sony EVI-D100 VISCA control class.
    Further documentation on the VISCA protocol (broken link):
    https://pro.sony.com/bbsccms/assets/files/mkt/remotemonitoring/manuals/rm-EVID100_technical_manual.pdf
    """
    
    values = ["1161h", "116Dh", "122Ah", "123Ch", "12F3h", "13C2h", "151Eh", "1536h", "1844h", "226Fh", "3F2Ah",
              "40AAh", "62C9h", "82C1h"]
    y = [
        20,
        18,
        16,
        14,
        12,
        10,
        8,
        6,
        4,
        2,
        1.5,
        1,
        0.5,
        0.1]

    def __init__(self, output='COM1'):
        """Instantiates the VISCA PTZ camera object.
        
        Then initializes camera object by connecting to serial port.
        :param output: Serial port string. (default: 'COM1')
        :type output: str
        """
        super(self.__class__, self).__init__(output=output)

    def _move(self, string, a1, a2):
        h1 = "%X" % a1
        h1 = '0' + h1 if len(h1) < 2 else h1

        h2 = "%X" % a2
        h2 = '0' + h2 if len(h2) < 2 else h2
        return self.comm(string.replace('VV', h1).replace('WW', h2))
    
    def _zero_pad(self, num: str, digit: int):
        """Pad any arbitrary number with zeros.
        
        :param num: The number to pad with zero.
        :param digit: The number's digit length to consider.
                      (Must be greater than or equal to the digit length of "num")
        :return: A string of padded number.
        """
        # Convert "num" to string
        num = str(num)
        
        # Apply zero-padding operation
        num_padded = ''
        if len(num) < digit:
            h = digit - len(num)
            for i in range(h):
                num_padded += '0'
        
        # Return the zero-padded value
        return num_padded + num
    
    def aperture_down(self):
        """Turn down the camera's aperture value (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040203FF')
    
    def aperture_reset(self):
        """Reset the camera's aperture to default value.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040200FF')
    
    def aperture_up(self):
        """Turn up the camera's aperture value (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040202FF')

    def autofocus(self):
        """Turns autofocus on.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043802FF')

    def autofocus_sens_high(self):
        """Changes autofocus sensitivity to high.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101045802FF')

    def autofocus_sens_low(self):
        """Changes autofocus sensitivity to low.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101045803FF')
    
    def backlight(self, toggle=1):
        """Turning the backlight compensation on/off.
        
        Defaults to "on" if invalid option is specified.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if toggle == False or toggle == 0:
            return self.comm('8101043303FF')
        else:
            return self.comm('8101043302FF')
    
    def bright_down(self):
        """Turn down the camera's brightness.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040D03FF')
    
    def bright_reset(self):
        """Reset the camera's brightness setting to default.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040D00FF')
    
    def bright_up(self):
        """Turn up the camera's brightness.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040D02FF')

    def cancel(self):
        """Cancels current command.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('81010001FF')
        
    def comm(self, com):
        """Sends hexadecimal string to serial port.

        :param com: Command string. Hexadecimal format.
        :type com: str
        :return: Success.
        :rtype: bool
        """
        super(self.__class__, self).command(com)

    def down(self, amount=5):
        """Modifies tilt to down.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = '0' + hs if len(hs) < 2 else hs
        s = '81010601VVWW0302FF'.replace('VV', str(15)).replace('WW', hs)
        return self.comm(s)

    def exposure_full_auto(self):
        """Changes exposure to full-auto.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043900FF')

    def focus_far(self, amount=5):
        """Focuses the camera to "far"
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104082PFF'.replace('P', hs)
        return self.comm(s)

    def focus_near(self, amount=5):
        """Focuses the camera to "near"
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104083PFF'.replace('P', hs)
        return self.comm(s)

    def focus_stop(self):
        """Stops any ongoing focus (near/far) movement.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040800FF')
    
    def freeze(self, toggle=1):
        """Freeze the camera immediately on or off.
        
        Defaults to "freeze on" if invalid option is specified.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if toggle == False or toggle == 0:
            return self.comm('8101046203FF')
        else:
            return self.comm('8101046202FF')
    
    def gain_down(self):
        """Turn down the camera's gain (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040C03FF')
    
    def gain_reset(self):
        """Reset the camera's gain value to default.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040C00FF')
    
    def gain_up(self):
        """Turn up the camera's gain (non-variable).
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040C02FF')

    def get_pan(self):
        """Get the PTZ's current absolute pan position.
        
        :return: The absolute pan value as an integer, converted from hex.
        """
        raw = self.inq('81090612FF')[5:12]
        return int(f'{raw[0]}{raw[2]}{raw[4]}{raw[6]}', 16)
    
    def get_power(self):
        """Get the PTZ's current standby state.
        
        :return: 1 if the PTZ is already on, 0 if it is in standby mode.
        """
        raw = self.inq('81090400FF')[4:6]
        if raw == '02':
            return 1
        elif raw == '03':
            return 0
        else:
			# Unexpected standby state return code.
            return -1

    def get_tilt(self):
        """Get the PTZ's current absolute tilt position.
        
        :return: The absolute tilt value as an integer, converted from hex.
        """
        raw = self.inq('81090612FF')[13:20]
        return int(f'{raw[0]}{raw[2]}{raw[4]}{raw[6]}', 16)

    def get_zoom(self):
        """Get the PTZ's current absolute zoom position.
        
        :return: The absolute zoom value as an integer, converted from hex.
        """
        raw = self.inq('81090447FF')[5:12]
        return int(f'{raw[0]}{raw[2]}{raw[4]}{raw[6]}', 16)
        
    def home(self):
        """Moves camera to home position.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('81010604FF')
    
    def inq(self, com):
        """Sends an inquiry message into the VISCA PTZ camera,
        then return any pending response buffer that comes afterwards.
        
        :param com: Command string (inquiry message). Hexadecimal format.
        :return: A string comprising the response packets.
        """
        # Clear any existing previous pending input buffer
        super(self.__class__, self).reset_input_buffer()
        
        # Send the inquiry message
        super(self.__class__, self).command(com)
        
        # Wait until any response packet is received
        x = ''
        while x == '':
            x = super(self.__class__, self).read()
            if x != '':
                break
        
        # Return the response packet
        return x
    
    def iris_down(self):
        """Turn down the camera's iris setting.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040B03FF')
    
    def iris_reset(self):
        """Reset the camera's iris setting to default.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040B00FF')
    
    def iris_up(self):
        """Turn up the camera's iris setting.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040B02FF')

    def left(self, amount=5):
        """Modifies pan speed to left.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        :rtype: bool
        """
        hex_string = "%X" % amount
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        s = '81010601VVWW0103FF'.replace('VV', hex_string).replace('WW', str(15))
        return self.comm(s)

    def left_down(self, pan=5, tilt=5):
        return self._move('81010601VVWW0102FF', pan, tilt)

    def left_up(self, pan=5, tilt=5):
        return self._move('81010601VVWW0101FF', pan, tilt)

    @staticmethod
    def multi_replace(text, rep):
        """Replaces multiple parts of a string using regular expressions.

        :param text: Text to be replaced.
        :type text: str
        :param rep: Dictionary of key strings that are replaced with value strings.
        :type rep: dict
        :return: Replaced string.
        :rtype: str
        """
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(list(rep.keys())))
        return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    def picture_effect_b_w(self):
        """Black and white picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046304FF')

    def picture_effect_mosaic(self):
        """Mosaic picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046306FF')

    def picture_effect_negative(self):
        """Negative picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046302FF')

    def picture_effect_off(self):
        """Off picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046300FF')

    def picture_effect_pastel(self):
        """Pastel picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046301FF')

    def picture_effect_sepia(self):
        """Sepia picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046303FF')

    def picture_effect_slim(self):
        """Slim picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046307FF')

    def picture_effect_solarize(self):
        """Solarize picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046305FF')

    def picture_effect_stretch(self):
        """Stretch picture effect.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046308FF')
    
    def power(self, toggle=1):
        """Turning the VISCA-based PTZ camera on or off.
        
        Defaults to "power on" if invalid option is specified.
        :return: True if successful, False if not.
        :rtype: bool
        """
        if toggle == False or toggle == 0:
            return self.comm('8101040003FF')
        else:
            return self.comm('8101040002FF')
    
    def preset_recall(self, memory):
        """Recall the assigned PTZ position from the memory bank 0-255.
        
        :return: True if successful, False if not.
        """
        num = memory
        num = 255 if num > 255 else num
        num = 0 if num < 0 else num
        # Convert 10-base decimal into hexadecimal
        hex_string = "%X" % num
        # Pad with zero, if less than two-digit
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        # Send the command
        s = '8101043F02PPFF'.replace('PP', hex_string)
        return self.comm(s)
    
    def preset_set(self, memory):
        """Set/save the current position of the PTZ into memory bank 0-255.
        
        :return: True if successful, False if not.
        """
        num = memory
        num = 255 if num > 255 else num
        num = 0 if num < 0 else num
        # Convert 10-base decimal into hexadecimal
        hex_string = "%X" % num
        # Pad with zero, if less than two-digit
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        # Send the command
        s = '8101043F01PPFF'.replace('PP', hex_string)
        return self.comm(s)

    def relative_position(self, pan, tilt, amount_pan, amount_tilt, direction_pan=1, direction_tilt=1):
        """Moves camera relative to current position.

        :param pan: Pan speed.
        :type pan: int
        :param tilt: Tilt speed.
        :type tilt: int
        :param amount_pan: Pan amount.
        :type amount_pan: int
        :param amount_tilt: Tilt amount.
        :type amount_tilt: int
        :param direction_pan: Pan direction (1 = right, -1 = left)
        :type direction_pan: int
        :param direction_tilt: Tilt direction (1 = up, -1 = down)
        :type direction_tilt: int
        :return: True if successful, False if not.
        :rtype: bool
        """
        if direction_pan != 1:
            amount_pan = 65532 - amount_pan
        if direction_tilt != 1:
            amount_tilt = 65500 - amount_tilt
        position_string = '81010603VVWW0Y0Y0Y0Y0Z0Z0Z0ZFF'
        pan_string = "%X" % amount_pan
        pan_string = pan_string if len(pan_string) > 3 else ("0" * (4 - len(pan_string))) + pan_string
        pan_string = "0" + "0".join(pan_string)

        tilt_string = "%X" % amount_tilt
        tilt_string = tilt_string if len(tilt_string) > 3 else ("0" * (4 - len(tilt_string))) + tilt_string
        tilt_string = "0" + "0".join(tilt_string)

        rep = {"VV": str(pan) if pan > 9 else "0" + str(pan), "WW": str(tilt) if tilt > 9 else "0" + str(tilt),
               "0Y0Y0Y0Y": pan_string, "0Z0Z0Z0Z": tilt_string}

        position_string = self.multi_replace(position_string, rep)
        return self.comm(position_string)

    def reset(self):
        """Resets camera.

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('81010605FF')

    def right(self, amount=5):
        """Modifies pan speed to right.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        """
        hex_string = "%X" % amount
        hex_string = '0' + hex_string if len(hex_string) < 2 else hex_string
        s = '81010601VVWW0203FF'.replace('VV', hex_string).replace('WW', str(15))
        return self.comm(s)

    def right_down(self, pan=5, tilt=5):
        return self._move('81010601VVWW0202FF', pan, tilt)

    def right_up(self, pan=5, tilt=5):
        return self._move('81010601VVWW0201FF', pan, tilt)

    def set_pan(self, val=0, speed=5):
        """Manually set the PTZ's absolute pan position.
        
        :param val: In integer, the absolute pan position (from -32767 to 32767).
        :param speed: In integer, the speed of the movement (0-24).
        :return: True if successful, False if not.
        """
        if val < -32767 or val > 32767 or type(val) != int:
            print('Invalid absolute pan value')
            return False
        
        # Calculating the parameter values
        if val < 0:
            val = 65535 + val
        
        # Preserving the current tilt value
        tilt = self.get_tilt()
        
        # Creating the parameter values
        p = self._zero_pad(hex(val)[2:], 4)
        t = self._zero_pad(hex(tilt)[2:], 4)
        s = self._zero_pad(hex(speed)[2:], 2)
        
        # Creating the command hex-string
        hs = f'81010602{s}{s}0{p[0]}0{p[1]}0{p[2]}0{p[3]}0{t[0]}0{t[1]}0{t[2]}0{t[3]}FF'
        
        # Sending the command
        return self.comm(hs)

    def set_pan_rel(self, val=0, speed=5):
        """Manually set the PTZ's relative pan position.
        
        :param val: In integer, the relative pan position (from -32767 to 32767).
        :param speed: In integer, the speed of the movement (0-24).
        :return: True if successful, False if not.
        """
        if val < -32767 or val > 32767 or type(val) != int:
            print('Invalid relative pan value')
            return False
        
        # Calculating the parameter values
        if val < 0:
            val = 65535 + val
        
        # Creating the parameter values
        p = self._zero_pad(hex(val)[2:], 4)
        t = '0000'
        s = self._zero_pad(hex(speed)[2:], 2)
        
        # Creating the command hex-string
        hs = f'81010603{s}{s}0{p[0]}0{p[1]}0{p[2]}0{p[3]}0{t[0]}0{t[1]}0{t[2]}0{t[3]}FF'
        
        # Sending the command
        return self.comm(hs)

    def set_tilt(self, val=0, speed=5):
        """Manually set the PTZ's absolute tilt position.
        
        :param val: In integer, the absolute tilt position (from -32767 to 32767).
        :param speed: In integer, the speed of the movement (0-24).
        :return: True if successful, False if not.
        """
        if val < -32767 or val > 32767 or type(val) != int:
            print('Invalid absolute tilt value')
            return False
        
        # Calculating the parameter values
        if val < 0:
            val = 65535 + val
        
        # Preserving the current pan value
        pan = self.get_pan()
        
        # Creating the parameter values
        p = self._zero_pad(hex(pan)[2:], 4)
        t = self._zero_pad(hex(val)[2:], 4)
        s = self._zero_pad(hex(speed)[2:], 2)
        
        # Creating the command hex-string
        hs = f'81010602{s}{s}0{p[0]}0{p[1]}0{p[2]}0{p[3]}0{t[0]}0{t[1]}0{t[2]}0{t[3]}FF'
        
        # Sending the command
        return self.comm(hs)

    def set_tilt_rel(self, val=0, speed=5):
        """Manually set the PTZ's relative tilt position.
        
        :param val: In integer, the relative tilt position (from -32767 to 32767).
        :param speed: In integer, the speed of the movement (0-24).
        :return: True if successful, False if not.
        """
        if val < -32767 or val > 32767 or type(val) != int:
            print('Invalid relative tilt value')
            return False
        
        # Calculating the parameter values
        if val < 0:
            val = 65535 + val
        
        # Preserving the current pan value
        pan = self.get_pan()
        
        # Creating the parameter values
        p = '0000'
        t = self._zero_pad(hex(val)[2:], 4)
        s = self._zero_pad(hex(speed)[2:], 2)
        
        # Creating the command hex-string
        hs = f'81010603{s}{s}0{p[0]}0{p[1]}0{p[2]}0{p[3]}0{t[0]}0{t[1]}0{t[2]}0{t[3]}FF'
        
        # Sending the command
        return self.comm(hs)
    
    def set_zoom(self, val=0):
        """Sets the absolute zoom value of the PTZ.
        
        :param val: In integer, the absolute zoom position (from 0 to 65535).
        :return: True if successful, False if not.
        """
        if val < 0 or val > 65535 or type(val) != int:
            print('Invalid absolute zoom value')
            return False
        
        # Creating the parameter values
        z = self._zero_pad(hex(val)[2:], 4)
        
        # Creating the command hex-string
        hs = f'810104470{z[0]}0{z[1]}0{z[2]}0{z[3]}FF'
        
        # Sending the command
        return self.comm(hs)
    
    def set_zoom_rel(self, val=0):
        """Sets the relative zoom value of the PTZ.
        
        :param val: In integer, the relative zoom position (from -32767 to 32767).
        :return: True if successful, False if not.
        """
        if val < -32767 or val > 32767 or type(val) != int:
            print('Invalid relative zoom value')
            return False
        
        # Preventing impossible zoom movements
        if (val + self.get_zoom()) < 0:
            val = 0 - self.get_zoom()
        
        # Calculating the parameter values
        val = self.get_zoom() + val
        if val < 0:
            val = 65535 + val
        
        # Creating the parameter values
        z = self._zero_pad(hex(val)[2:], 4)
        
        # Creating the command hex-string
        hs = f'810104470{z[0]}0{z[1]}0{z[2]}0{z[3]}FF'
        
        # Sending the command
        return self.comm(hs)

    def stop(self):
        """Stops camera movement (pan/tilt).

        :return: True if successful, False if not.
        """
        return self.comm('8101060115150303FF')

    def up(self, amount=5):
        """Modifies tilt speed to up.

        :param amount: Speed (0-24)
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = '0' + hs if len(hs) < 2 else hs
        s = '81010601VVWW0301FF'.replace('VV', str(15)).replace('WW', hs)
        return self.comm(s)

    def white_balance_auto(self):
        """White balance: Automatic mode

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043500FF')

    def white_balance_indoor(self):
        """White balance: Indoor mode

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043501FF')

    def white_balance_outdoor(self):
        """White balance: Outdoor mode

        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101043502FF')

    def wide_169(self):
        """Wide mode setting: 16:9

        Stretches picture to 16:9 format.
        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046002FF')

    def wide_cinema(self):
        """Wide mode setting: Cinema

        Places black bars above and below picture. Otherwise maintains resolution.
        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046001FF')

    def wide_off(self):
        """Wide mode setting: Off

        Returns to original 640x480 resolution.
        :return: True if successful, False if not.
        :rtype: bool
        """
        return self.comm('8101046000FF')

    def zoom_in(self, amount=5):
        """Zooms the camera lens in.
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104072PFF'.replace('P', hs)
        return self.comm(s)

    def zoom_out(self, amount=5):
        """Zooms the camera lens out.
        
        :param amount: Speed (0-7), default=5
        :return: True if successful, False if not.
        """
        hs = "%X" % amount
        hs = 7 if int(hs, 16) > 7 else hs
        hs = 0 if int(hs, 16) < 0 else hs
        s = '810104073PFF'.replace('P', hs)
        return self.comm(s)

    def zoom_stop(self):
        """Stops any ongoing zoom (tele/wide) movement.
        
        :return: True if successful, False if not.
        """
        return self.comm('8101040700FF')
