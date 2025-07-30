# SPDX-FileCopyrightText: 2025 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Simple test script for 2.9" 296x128 display. This example runs it in 2bit grayscale mode."""

import time

import board
import busio
import displayio
from fourwire import FourWire

import adafruit_ssd1680

displayio.release_displays()

# This pinout works on a MagTag with the newer screen and may need to be altered for other boards.
spi = busio.SPI(board.EPD_SCK, board.EPD_MOSI)  # Uses SCK and MOSI
epd_cs = board.EPD_CS
epd_dc = board.EPD_DC
epd_reset = board.EPD_RESET
epd_busy = board.EPD_BUSY

display_bus = FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
time.sleep(1)

ti_290mfgn_gray4_lut_code = (
    b"\x2a\x60\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L0
    b"\x20\x60\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L1
    b"\x28\x60\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L2
    b"\x00\x60\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L3
    b"\x00\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L4
    b"\x00\x02\x00\x05\x14\x00\x00"  # TP, SR, RP of Group0
    b"\x1e\x1e\x00\x00\x00\x00\x01"  # TP, SR, RP of Group1
    b"\x00\x02\x00\x05\x14\x00\x00"  # TP, SR, RP of Group2
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group3
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group4
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group5
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group6
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group7
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group8
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group9
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group10
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP of Group11
    b"\x24\x22\x22\x22\x23\x32\x00\x00\x00"  # FR, XON
)

if len(ti_290mfgn_gray4_lut_code) != 153:
    raise ValueError("ti_290mfgn_gray4_lut_code is not the correct length")

# For issues with display not updating top/bottom rows correctly set colstart to 8, 0, or -8
display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=296,
    height=128,
    busy_pin=epd_busy,
    rotation=270,
    colstart=0,
    vcom=0x28,
    vsh2=0xAE,
    custom_lut=ti_290mfgn_gray4_lut_code,
    grayscale=True,
)

g = displayio.Group()

pic = displayio.OnDiskBitmap("/display-ruler-640x360.bmp")
t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
g.append(t)

display.root_group = g

display.refresh()

print("refreshed")

time.sleep(display.time_to_refresh + 5)
# Always refresh a little longer. It's not a problem to refresh
# a few seconds more, but it's terrible to refresh too early
# (the display will throw an exception when if the refresh
# is too soon)
print("waited correct time")


# Keep the display the same
while True:
    time.sleep(10)
