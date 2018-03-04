# OctoPrint-Badger

Prints 2D Badges/Labels.

Uses OctoPrint system to allow for "Do No Hack" labels to be printed on a Dymo Label Writer (for MakeSpace) using RFID tags.

Not really used for 3D printing unless you wish to modify and automate to print labels for when a print is finished or something.

## Setup

Hardware setup:

* Raspberry Pi 3
* Dymo LabelWriter 450
* IB Technology Micro RWD RFID reader (for Makespace door kep)
* 2x 28mm Arcade buttons with LEDs (Optional)
* Pi Power Hat (https://github.com/Tinamous/PiPowerHat) (optional) or 5V DC supply for Raspberry Pi
* Labels, lots of...

### Buttons:

Left Button:

* Switch Pin 1: GND
* Switch Pin 2: GPIO 26
* LED Pin 1: GND
* LED Pin 2: via 82R resistor to GPIO 16


Right Button: 

* Switch Pin 1: GND
* Switch Pin 2: GPIO 21
* LED Pin 1: GND
* LED Pin 2: via 82R resistor to GPIO 20

LED Indicator:

* GPIO 11 with 1k resistor going to GND (this is build on-board the Pi Power Hat)


### Software Installation

* Download and install OctoPi (https://octoprint.org/download/)
* Follow the Getting Started Guide for OctoPi.
* Install Cups
* Download and install the Dymo 450


#### Install CUPS:

sudo apt-get install libcups2-dev libcupsimage2-dev g++ cups cups-client

#### Install Dymo 450 Printer

The driver can be downloaded from:

http://www.dymo.com/en-US/dymo-label-sdk-and-cups-drivers-for-linux-dymo-label-sdk-cups-linux-p--1#

For convenience it's also in this repository:

* wget https://github.com/Tinamous/OctoPrint-Badger/raw/master/Notes/dymo-cups-drivers-1.4.0.tar.gz

* tar xvf dymo-cups-drivers-1.4.0.tar.gz
* cd dymo-cups-drivers-1.4.0.5/
* sudo ./configure
* sudo make
* sudo make install

Then add the Pi user to the printing group and enable remote admin

* sudo usermod -a -G lpadmin pi
* cupsctl --remote-admin

You should now be able to open a browser to the CUPS server:

* https://octopi.local:631/
* Add the printer (Administration/Add Printer/Select the 450).
* Select the label size (99012), quality (300x600) and select Barcode and Graphics as the default

#### Install OctoPrint-Badger plugin

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/Tinamous/OctoPrint-Badger/archive/master.zip
    
    
The registration plug-in will most likely be needed as well, grab that from https://github.com/Tinamous/OctoPrint-Registration

Once installed configure the pluging settings to use the appropriate printer and RFID reader.


#### Remove Unwanted OctoPrint bits.

* cd ~/.octoprint/
* sudo nano config.yaml

Add/Update the following:

appearance:
  components:
    disabled:
      tab:
      - temperature
      - gcodeviewer
      - terminal
      - control
      - plugin_pipower
      - timelapse
      sidebar:
      - connection
      - state
      - files
    order:
      tab:
      - plugin_whosprinting




## Configuration

This is work in progress. Requires CUPS support to be installed. Please see the Notes folder for the time being.


