# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
# SPDX-FileCopyrightText: 2025 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Simple test script for 2.9" 296x128 display. This example runs it in 2bit grayscale mode.

Automatically detects whether the MagTag has the original FPC-A005 panel or the
newer FPC-7519rev.b panel by reading the SSD1680 User ID register before the SPI
bus is initialized.
"""

import time

import board
import busio
import displayio
from fourwire import FourWire

import adafruit_ssd1680

displayio.release_displays()

panel_id = adafruit_ssd1680.detect_ssd1680_panel(
    board.EPD_MOSI, board.EPD_SCK, board.EPD_CS, board.EPD_DC, board.EPD_RESET
)
print(f"SSD1680 User ID first byte: 0x{panel_id:02x}")

if panel_id == 0x00:
    print("Detected: FPC-A005 panel (legacy)")
    vcom = 0x28
    colstart = 0
    lut = adafruit_ssd1680.FPC_A005_LUT
else:
    print("Detected: FPC-7519rev.b or newer panel")
    vcom = 0x24
    colstart = 8
    lut = adafruit_ssd1680.FPC7519_LUT

spi = busio.SPI(board.EPD_SCK, board.EPD_MOSI)
display_bus = FourWire(
    spi, command=board.EPD_DC, chip_select=board.EPD_CS, reset=board.EPD_RESET, baudrate=1000000
)
time.sleep(1)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=296,
    height=128,
    busy_pin=board.EPD_BUSY,
    rotation=270,
    colstart=colstart,
    vcom=vcom,
    vsh2=0xAE,
    custom_lut=lut,
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
print("waited correct time")

while True:
    time.sleep(10)
