#!/usr/bin/python3

# Simple software timer for a switch on the piface digital io

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

# Import libraries
from time import time
import pifacedigitalio


# Define class
class Switch:
    # Code to run when class is created
    def __init__(self, pin):
        self.pin = pin
        self.state = False
        self.lastTime = 0
        self.lastOff = 0
        self.pfio = pifacedigitalio.PiFaceDigital()
        self.state = False
        self.lastTime = time()

    # Method for a timed flipflop
    def timed(self, freq, duration):
        # Deactivate if time is up
        if (time() - self.lastTime) >= duration and self.state == True:
            # Set switch to off
            return self.write(False)
        
        # Activate if wait is up
        elif (time() - self.lastTime) >= freq and self.state == False:
            # Set switch to on
            return self.write(True)

    # Method to turn a switch on or off
    def write(self, state):
        # If we want to turn on...
        if state:
            self.pfio.output_pins[self.pin].turn_on()
            
        # Otherwise assume turn off
        else:
            self.pfio.output_pins[self.pin].turn_off()
            
        # Save the time and state of this change to memory
        self.lastTime = time()
        self.state = self.pfio.output_pins[self.pin].value
        
        # Return the new state
        return self.state

    # Method to turn all switches off when code is cancelled
    def __del__(self):
        self.write(False)
        print('\nSwitch %d off\n' % self.pin)
