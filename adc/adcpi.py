##!/usr/bin/env python3

# abelectronics ADC Pi V2 driver

# Some code taken and rewritten from the abelectronics Python 2.7 driver

# Copyright (C) 2014  Simon Howroyd
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

#############################################################################

# Import Libraries
from quick2wire.i2c import I2CMaster, writing_bytes, reading


# Define Class
class AdcPi2:
    # Code to run when class is created
    def __init__(self, res=12):
        # Check if user inputted a valid resolution in constructor
        if res != 12 and res != 14 and res != 16 and res != 18:
            # Raise an exception to crash the code
            raise IndexError('Incorrect ADC Resolution')
        else:
            # Set the resolution to memory
            self.__res = res

        # Build default address and configuration register of the ADC
        self.__config = [[0x68, 0x90],
                         [0x68, 0xB0],
                         [0x68, 0xD0],
                         [0x68, 0xF0],
                         [0x69, 0x90],
                         [0x69, 0xB0],
                         [0x69, 0xD0],
                         [0x69, 0xF0]]

        # Set resolution in configuration register
        for x in range(len(self.__config)):
            self.__config[x][1] = self.__config[x][1] | int((res - 12) / 2) << 2

        # Set the calibration multiplier
        self.__varDivisor = 0b1 << (res - 12)
        self.__varMultiplier = (2.495 / self.__varDivisor) / 1000

    # Method to change the channel we wish to read from
    @staticmethod
    def __changechannel(config):
        # Using the I2C databus...
        with I2CMaster(1) as master:
            master.transaction(
                writing_bytes(config[0], config[1]))

    # Method to read adc
    @staticmethod
    def __getadcreading(config, multiplier, res):
        # Using the I2C databus...
        with I2CMaster(1) as master:
            # Calculate how many bytes we will receive for this resolution
            numBytes = int(max(0, res / 2 - 8) + 3)

            # Initialise the ADC
            adcreading = master.transaction(
                writing_bytes(config[0], config[1]),
                reading(config[0], numBytes))[0]

            # Wait for valid data **blocking**
            while (adcreading[-1] & 128):
                adcreading = master.transaction(
                    writing_bytes(config[0], config[1]),
                    reading(config[0], numBytes))[0]

            # Shift bits to product result
            if numBytes is 4:
                t = ((adcreading[0] & 0b00000001) << 16) | (adcreading[1] << 8) | adcreading[2]
            else:
                t = (adcreading[0] << 8) | adcreading[1]

            # Check if positive or negative number and invert if needed
            if adcreading[0] > 128:
                t = ~(0x020000 - t)

            # Return result
            return t * multiplier

    # External getter - call this to receive data
    def get(self, channel):
        # Change adc setting to the channel we want to read
        self.__changechannel(self.__config[channel])
        
        # Read and return the data
        return self.__getadcreading(self.__config[channel], self.__varMultiplier, self.__res)
