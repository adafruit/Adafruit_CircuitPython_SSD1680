# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: Unlicense


"""Simple test script for Adafruit 2.9" Tri-Color eInk Display Breakout
Supported products:
  * Adafruit 2.9" Tri-Color eInk Display Breakout
    * https://www.adafruit.com/product/1028

"""

import time

import board
import displayio
from fourwire import FourWire

import adafruit_ssd1680

displayio.release_displays()

# This pinout works on a Metro M4 and may need to be altered for other boards.
spi = board.SPI()  # Uses SCK and MOSI
epd_cs = board.D9
epd_dc = board.D10
epd_reset = board.D5
epd_busy = board.D6

display_bus = FourWire(spi, command=epd_dc, chip_select=epd_cs, baudrate=1000000)
time.sleep(1)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=296,
    height=128,
    highlight_color=0xFF0000,
    rotation=270,
)

g = displayio.Group()


pic = displayio.OnDiskBitmap("/display-ruler-640x360.bmp")

t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)

g.append(t)

display.root_group = g

display.refresh()

print("refreshed")

time.sleep(120)
