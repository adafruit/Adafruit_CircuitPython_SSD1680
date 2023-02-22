# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: Unlicense


"""Simple test script for 2.13" 250x122 eInk Display FeatherWing
Supported products:
  * Adafruit 2.13" Tri-Color eInk Display FeatherWing
    * https://www.adafruit.com/product/4814
  * Adafruit 2.13" Mono eInk Display FeatherWing
    * https://www.adafruit.com/product/4195


"""

import time
import board
import displayio
import adafruit_ssd1680

displayio.release_displays()

# This pinout works on a Metro M4 and may need to be altered for other boards.
spi = board.SPI()  # Uses SCK and MOSI
epd_cs = board.D9
epd_dc = board.D10

display_bus = displayio.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, baudrate=1000000
)
time.sleep(1)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    colstart=8,
    width=250,
    height=122,
    highlight_color=0xFF0000,
    rotation=270,
)

g = displayio.Group()

with open("/display-ruler.bmp", "rb") as f:
    pic = displayio.OnDiskBitmap(f)

    t = displayio.TileGrid(
        pic, pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter())
    )

    g.append(t)

    display.show(g)

    display.refresh()

    print("refreshed")

    time.sleep(120)
