# OctoPrint NeoPixel Illumination

This plugin will allow fairly comprehensive control of NeoPixels from Octoprint.

- Use your Raspberry Pi to power and control your NeoPixels. (I have tested powering up to 25 pixels from a Raspberry Pi 4).
- Change color and intensity from a color picker dialog.
- Intercept GCODE [M150](https://marlinfw.org/docs/gcode/M150.html) commands and execute them on the Raspberry Pi.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/brettvitaz/OctoPrint-Neopixel_Illumination/archive/master.zip

## Preparing your Raspberry Pi

### Identify desired control pin

This can change based on your needs, but a recommended pin is [GPIO 18](https://pinout.xyz/pinout/pin12_gpio18#).

### Add the API to the system startup

Instructions coming...

### Plug in your NeoPixels

If running a small number of pixels, they can be powered directly from the Raspberry Pi.

Please carefully review [these instructions](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring) for wiring your NeoPixel strip to the Raspberry Pi. 

*n.b. I have witnessed damage to both Raspberry Pis and Arduinos when improperly wired.*

### If using GPIO 10, ensure that SPI mode is enabled.

Log in to your Raspberry Pi:

```bash
$ ssh pi@octopi.local
```

Enable SPI mode from Raspi Config:

```bash
$ sudo raspi-config
```

Select `4. Interface Options`, `P4. SPI`, `Yes`, `OK`.

## Configuration

Open the OctoPrint configuration dialog and select Plugins | NeoPixel Illumination.

- Enter the pixel color order for your NeoPixel controller.
- Enter the [GPIO pin](https://pinout.xyz/). 
- Enter the number of pixels in the device or strip.
- Choose if you want to parse GCODE for M150 commands.
- Enable the plugin.

Choosing a color from the color picker will save it as the start-up color.
