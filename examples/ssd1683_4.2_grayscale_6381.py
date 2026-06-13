# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""4-gray grayscale example for the Adafruit 4.2" 400x300 E-Ink Display (#6381).

Ribbon Identifier: FPC-190, colstart=0.
Tested on Adafruit Feather RP2040 ThinkInk.
"""

import time

import board
import busio
import displayio
from fourwire import FourWire

import adafruit_ssd1680

displayio.release_displays()

spi = busio.SPI(board.EPD_SCK, board.EPD_MOSI)
display_bus = FourWire(
    spi,
    command=board.EPD_DC,
    chip_select=board.EPD_CS,
    reset=board.EPD_RESET,
    baudrate=1000000,
)
time.sleep(1)

display = adafruit_ssd1680.SSD1683(
    display_bus,
    width=400,
    height=300,
    busy_pin=board.EPD_BUSY,
    rotation=270,
    colstart=0,
    vcom=0x30,
    custom_lut=adafruit_ssd1680.SSD1683_GRAY4_LUT,
)

W, H = 400, 300
bmp = displayio.Bitmap(W, H, 4)
pal = displayio.Palette(4)
pal[0] = 0xFFFFFF  # white
pal[1] = 0xAAAAAA  # light gray
pal[2] = 0x555555  # dark gray
pal[3] = 0x000000  # black

COL = W // 4
for y in range(H):
    for x in range(W):
        bmp[x, y] = min(x // COL, 3)

g = displayio.Group()
g.append(displayio.TileGrid(bmp, pixel_shader=pal))
display.root_group = g

print("Refreshing...")
display.refresh()
print("Done.")

time.sleep(display.time_to_refresh + 5)

while True:
    time.sleep(10)
