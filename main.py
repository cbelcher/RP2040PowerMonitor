# v10.5 5/11/2026
# Starting to test reset button interrupt functionality.

# Adding ALERT pin to RP2040-Zero using GP7.
# Working on adding interrupt handling for this pin.

# Found an interesting issue with the RP2040-Zero.  These are the no-name clones.
# Looks like the batch of 6 I purchased have different USB PIDs.
# Couple return: VID: 2E8A, PID: 0005 (This is the same as the official Raspberry Pi Pico)
# Others return: VID: 2E8A, PID: 101F (This is assigned to Waveshare, the manufacturer of the RP2040-Zero)
# Had to account for this in my Windows app in the AutoDetectPico function.


# Waveshare RP2040-Zero, AITRIP 2.4" SSD1309 128x64 OLED LCD Display and DONGKER INA260 example
# SSD1309 based OLED display using I2C on address 0x3C & INA260 Address 0x40

# DONGKER INA260 Current/Voltage/Power Sensor Driver for Raspberry Pi Pico
# INA260 Pin	    RP2040-Zero Pin		Zero GPIO       I2C             Description
# ----------------------------------------------------------------------------------------
# VCC               Pin 21                  3V3                         3.3V Power Out
# GND               Pin 20                  GND                         Ground
# SCL               Pin 10                  GP9         I2C0 SCL        I2C Clock
# SDA               Pin 9                   GP8         I2C0 SDA        I2C Data
# ALERT             Pin 8                   GP7                         Alert (Added in v9.0)


#AITRIP 2PCS 2.4" SSD1309 128x64 OLED LCD Display Module 4 Pin IIC/I2C
# I2C Address: 0x3c
# SSD1390 OLED Pin	RP2040-Zero Pin		Zero GPIO       I2C             Description
# ---------------------------------------------------------------------------------
# SDA               Pin 9                   GP8         I2C0 SDA        I2C Data
# SCL               Pin 10                  GP9         I2C0 SCL        I2C Clock
# VDD               Pin 21                  3V3                         3.3V Power Out
# GND               Pin 20                  GND                         Ground


import struct
import sys

from machine import I2C, Pin
import time
import ustruct
from ssd1309 import Display
from xglcd_font import XglcdFont

# I'm having issues getting this RP2040-Zero to run main.py.
# Don't know what is going on just yet.

# Tried this, but didn't do anything.
# Wait 1 seconds for the USB connection to be established before starting the main loop.
time.sleep(1)



# INA260 Power Monitor Class
class INA260:
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address

        # Register Addresses
        self._REG_CONFIG  = 0x00
        self._REG_CURRENT = 0x01
        self._REG_VOLTAGE = 0x02
        self._REG_POWER   = 0x03
        # Set Mask/Enable for Alert Pin to trigger on Over Current Limit and Latch the Alert until cleared.
        self._REG_MASK_ENABLE = 0x06

        # Unpacked with big-endian ">H" format
        # Conversion Ready flag (bit 3) is set to 1 when a new conversion result is ready.
        # The only time bit-3 is a 0, is when the INA is initially powered up.
        
        # Set Enable bit (bit 15) to 1 to enable the Alert function, and set the Over Current Limit
        # flag (bit 0) to 1 to trigger an alert when the current exceeds the limit.
        self.i2c.writeto_mem(self.address, self._REG_MASK_ENABLE, b'\x80\x01')


        # Examples of Alert Limit Register values:
        # The INA260 can exceed 15 A continouse handling limit for brief periods of time
        # Figure 22 of the datasheet 100A for 20ms and 50 A's for up to 1 second
        # ., but the alert limit register is only 16 bits, so the maximum value that can be set is 65535 decimal or FFFFh hex.
        # 2.5 A (2.5 A / 1.25 mA) = 2000 decimal = 0x07D0 hex.
        # 14.5 A (14.5 A / 1.25 mA = 11600 decimal = 0x2D50 hex.
        # 16.0 A (16 A / 1.25 mA) = 12800 decimal = 0x3200 hex.
        # 50.0 A (50 A / 1.25 mA) = 40000 decimal = 0x9C40 hex.
        self._REG_ALERT_LIMIT = 0x07
        # Set Alert Limit Register to 16 A.  (16 A / 1.25 mA) = 12800 decimal and 3200h
        self.i2c.writeto_mem(self.address, self._REG_ALERT_LIMIT, b'\x32\x00')

    def _read_register(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        return ustruct.unpack('>h', data)[0]

    def get_voltage(self):
        return self._read_register(self._REG_VOLTAGE) * 0.00125

    def get_current(self):
        return self._read_register(self._REG_CURRENT) * 0.00125

    def get_power(self):
        return self._read_register(self._REG_POWER) * 0.010
    
    # Method to read value of the Mask/Enable register for debugging purposes.
    def get_mask_enable(self):
        data = self.i2c.readfrom_mem(self.address, self._REG_MASK_ENABLE, 2)
        #return ustruct.unpack('>h', data)[0]  <- Needs to be >H which is big-endian unsigned short
        return ustruct.unpack('>H', data)[0]

    #Method to read value of the Alert Limit register for debugging purposes.
    def get_alert_limit(self):
        data = self.i2c.readfrom_mem(self.address, self._REG_ALERT_LIMIT, 2)
        return ustruct.unpack('>H', data)[0]
    
    # Method to read value of the Configuration register for debugging purposes.
    def get_config(self):
        data = self.i2c.readfrom_mem(self.address, self._REG_CONFIG, 2)
        return ustruct.unpack('>H', data)[0]

# SSD1309 OLED Display Class
class SSD1309:
    def __init__(self, i2c, address=0x3c):
        self.i2c = i2c
        self._display = Display(i2c=i2c, address=address)
        self.unispace = XglcdFont('fonts/Unispace12x24.c', 12, 24)
        #self.Bally = XglcdFont('fonts/Bally.c', 7, 9)
        self.Bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
    
    def update_display(self, voltage, current, power):
        self._display.draw_text(x=0, y=0, text="V: {:.3f}".format(voltage), font=self.unispace)
        self._display.draw_text(x=0, y=20, text="I: {:.3f}".format(current), font=self.unispace)
        self._display.draw_text(x=0, y=40, text="P: {:.3f}".format(power), font=self.unispace)
        self._display.present()

# Initialize I2C bus for both INA260 and SSD1309
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

# Initialize INA260 sensor
ina260 = INA260(i2c)

# Initialize SSD1309 OLED display
oled = SSD1309(i2c)

# GP 7 is connected to the INA260's ALERT pin
# Set Pin 7 as an input with a pull-up resistor (active low)
# The INA260's ALERT pin is an open-drain active low.
# The INA260 will pull this pin to GND when the current exceeds the alert limit.
# GP 7 will be used to trigger an interrupt to alert the user when the current exceeds the limit.
alert_pin = Pin(7, Pin.IN, Pin.PULL_UP)

# Set the OCL_tripped flag to False initially.
OCL_tripped = False

def OCL_alert_handler(pin):
    # This runs the instant the ALE pin goes LOW
    print("Interrupt triggered on pin:", pin)
    print("ALERT: Overcurrent detected!")
    # Update global variable or flag
    global OCL_tripped
    OCL_tripped = True

# Attach the interrupt
alert_pin.irq(trigger=Pin.IRQ_FALLING, handler=OCL_alert_handler)


# Reset OCL Alert Interrupt
# To reset the OCL alert, the user must press the reset button which is connected to GP6.
reset_pin = Pin(6, Pin.IN, Pin.PULL_UP)


def reset_handler(pin):
    # This runs the instant the ALE pin goes LOW
    print("Interrupt triggered on pin:", pin)
    print("INA ALERT Reset button pressed!")
    # Read the Mask/Enable register to clear the Alert flag and reset the Alert pin to high.
    print(f"Mask/Enable Value before reading: {ina260.get_mask_enable():04X}h")
    print("In theory this should clear the Alert flag and set the Alert pin back to high.")
    print(f"Mask/Enable Value after printing: {ina260.get_mask_enable():04X}h")
    print("Reading the Mask/Enable register to clear the Alert flag...")
    ina260._read_register(ina260._REG_MASK_ENABLE)
    print(f"Mask/Enable Value after reading: {ina260.get_mask_enable():04X}h")
    # Update global variable or flag
    global OCL_tripped
    OCL_tripped = False
    print("Clear display")
    oled._display.clear()

# Attach the interrupt
reset_pin.irq(trigger=Pin.IRQ_FALLING, handler=reset_handler)

def main():
    print("Starting main loop. Waiting for alerts...")
    # Read Mask/Enable register to clear the Alert flag and reset the Alert pin to high before starting the main loop.
    mask_enable_value = ina260.get_mask_enable()
    #print("Initial Mask/Enable Value: {:04X}h".format(mask_enable_value))
    print(f"Initial Mask/Enable Value: {mask_enable_value:04X}h")
    print(f"This should now be 8001h or 8009h after reading the register: {ina260.get_mask_enable():04X}h")
    print(f"Alert Limit Value: {ina260.get_alert_limit():04X}h")


    try:
        while True:
            # Testing to see changing from if OCL_tripped: to while OCL_tripped: to continuously display the alert message until the user presses the reset button to clear the alert and reset the Alert pin back to high.
            # if OCL_tripped:
            while OCL_tripped:
                print("OCL Tripped!")
                print(f"Alert Pin State: {alert_pin.value()}")
                print(f"Alert Limit Value: {ina260.get_alert_limit():04X}h")
                print(f"OCL Mask/Enable Value: {ina260.get_mask_enable():04X}h")
                # current = ina260.get_current()
                print(f"V: {voltage:.3f}, I: {current:.3f}, P: {power:.3f}")
                oled._display.clear()
                oled._display.draw_text(x=1, y=10, text="ALERT: Overcurrent", font=oled.Bally)
                oled._display.draw_text(x=30, y=20, text="Protection!", font=oled.Bally)
                oled._display.draw_text(x=30, y=35, text="Power Cycle", font=oled.Bally)
                oled._display.draw_text(x=40, y=45, text="to Reset", font=oled.Bally)
                oled._display.present()
                while OCL_tripped:
                    time.sleep(2) # Sleep for 2 seconds to prevent flooding the console with messages while the alert is active.
                # break
        
            else:
                # Read voltage, current, and power from INA260 sensor
                voltage = ina260.get_voltage()
                current = ina260.get_current()
                power = ina260.get_power()
                # Update OLED display with the latest readings
                oled.update_display(voltage, current, power)
                time.sleep_ms(50) # Update 20 times per second
                # Send readings to stdout debugging and via USB to Windows application.
                sys.stdout.write("V: {:.3f}, I: {:.3f}, P: {:.3f}\n".format(voltage, current, power))
            # print("Entering main data acquisition loop...")
            # Call Mask/Enable register and Alert Limit register read methods for debugging purposes.
            # mask_enable_value = ina260.get_mask_enable()
            # alert_limit_value = ina260.get_alert_limit()
            # print("Mask/Enable Value: {:04X}".format(mask_enable_value))
            # print("Alert Limit Value: {:04X}".format(alert_limit_value))
            # Output value of configuration register for debugging purposes.
            # Read the Configuration Register value for debugging purposes.
            # config_value = ina260.get_config()
            # print("Configuration Value: {:04X}".format(config_value))

    except KeyboardInterrupt:
            print("Program stopped by user.")
            oled._display.cleanup()

main()
