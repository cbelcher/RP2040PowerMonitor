# Pico Power Monitor RP2040-Zero Micro Python Files


This the repo contains the files needed to run the hardware side of things, for the Pico Power Monitor.

## Project is broken up into 4 sub-projects.

  - MicroPhython code to drive the hardware. - This Repo.
      This is the project that runs on the RP2040-Zero.  Current MicroPython firmware 1.28.
    
  - KiCAD Custom PCB Design
    - Repo: /PicoPowerMonitor_KiCad (Direct link [here](https://github.com/cbelcher/PicoPowerMonitor_KiCad))

	- PCBWay Shared Projects (Direct link [here](https://www.pcbway.com/project/shareproject/Pico_Power_Monitor_e0ff12c4.html))

  - PicoPowerMonitor - This is the Windows 11 application, completely optional.  The PicoPowerMonitor can and does run without this application.
  
	- Repo: /PicoPowerMonitor (Direct link [here](https://github.com/cbelcher/PicoPowerMonitor))
 
  - FreeCAD 3D Printed Case Design. (Project should be uploaded as soon as I get some time.)

## Key Features

- Instantiates I2C communications to OLED display and the TI's INA260 Power Montior IC.
- Sets up the TI INA260's OCL (Over Current Limit) register.  Default 16 A.  Configurable.
- Reads the INA260's registers 100 times / second for Curent, Voltage and Power values.
- Updates OLED Display with INA260 readings.
- Interupt handler to shut down the Infineon BSC007N04LS6 N-Channel MOSFET during an OCL event and update the 2.4" OLED Display to notify user.
- Interupt handler to take the input of momentary SPST reset button.  Clears the INA260 ALERT and restarts main loop.
- Streams current and voltage readings to native Windows 11 application.

## Installation

- Flash UF2 bootloader  uf2 can be downloaded [here](https://micropython.org/download/WAVESHARE_RP2040_ZERO/))
- Pick your IDE of choice, Thonny, VSC...
- Upload the files to the RP-2040-Zero.  If this is all new to you, Thonny is as easy as it gets.
-   - Direct link [here](https://thonny.org/))
    - Need to maintain fonts directory structure.  You don't, this will not run!
    - i2c_scan.py is not required, just there to verify the RP2040-Zero can see the display and the INA260 on the I2C bus.
    - main.py (named as such as to run on power-up)  This is the core script.
    - ssd1309.py is the open-source SPI & I2C display driver by rdagger / micropython-ssd1309
    - xglcd_font.py handles the GLCD Fonts, not sure who to give credit for this work.
    - Make sure the script runs.
    - After that disconnect from PC and reconnect, main.py should fire up and the display should come to life.
 
## Images

-Thonny screenshot
<p align="center">
<img width="1310" height="1057" alt="Screenshot 2026-06-22 05 42 31" src="https://github.com/user-attachments/assets/f696248e-139f-42df-8e4e-2d77d1463952" />
</p>

- OLED display
<p align="center">
<img width="4032" height="3024" alt="IMG_2811" src="https://github.com/user-attachments/assets/9928a3e3-ba69-45ef-ba5b-47d284369fcf" />
</p>



## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

## Acknowledgments

* Built as a dedicated utility for hardware repair professionals and electrical engineers.
* Display powered by open-source driver by rdagger / micropython-ssd1309.  https://github.com/rdagger/micropython-ssd1309
