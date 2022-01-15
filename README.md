# OctoPrint Neopixel Illumination

Control Neopixels from Octoprint.
The ultimate goal of this project is to intercept neopixel gcode commands and execute them on the Raspberry Pi.

**TODO:** Describe what your plugin does.

Currently, all it does is turn your neopixels teal. More to come...

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/brettvitaz/OctoPrint-Neopixel_Illumination/archive/master.zip

### Preparing your RaspberryPi

#### Ensure that SPI mode is enabled.

Log in to your Raspberry Pi:

```bash
$ ssh octopi.local
```

Enable SPI mode from Raspi Config:

```bash
$ sudo raspi-config
```

Select `4. Interface Options`, `P4. SPI`, `Yes`, `OK`.

#### Plug in your Neopixels

If running a small number of pixels, they can be powered directly from the Raspberry Pi.

Plug in the leads to:

- +5v to physical pin 2
- GND to physical pin 6
- Data Input to GPIO 10 (physical pin 19)


## Configuration

**TODO:** Describe your plugin's configuration options (if any).

Configuration options will exist for start-up mode (color, brightness, etc.), intercepting gcode, maybe others...
