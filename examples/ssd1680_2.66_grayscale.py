# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""4-gray grayscale example for the Adafruit 2.66" 296x152 E-Ink Display (#6392).

Displays a 4-level gray ramp (white / light gray / dark gray / black) across the
full panel. Uses the FPC7519 waveform LUT, which transfers cleanly to this panel.

Tested on Adafruit Feather RP2040 ThinkInk with a panel labeled FPC-A003 1S on
the ribbon connector.

Hardware: connect the 24-pin FPC ribbon directly to the ThinkInk board's ZIF connector.
No external wiring required.
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

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=296,
    height=152,
    busy_pin=board.EPD_BUSY,
    rotation=270,
    colstart=0,
    vcom=0x1C,
    vsh2=0xAE,
    custom_lut=adafruit_ssd1680.FPC7519_LUT,
    grayscale=True,
)

W, H = 296, 152
bmp = displayio.Bitmap(W, H, 4)
pal = displayio.Palette(4)
pal[0] = 0xFFFFFF  # white
pal[1] = 0xAAAAAA  # light gray
pal[2] = 0x555555  # dark gray
pal[3] = 0x000000  # black

COL = W // 4
for y in range(H):
    for x in range(W):
        bmp[x, y] = x // COL

g = displayio.Group()
g.append(displayio.TileGrid(bmp, pixel_shader=pal))
display.root_group = g

print("Refreshing...")
display.refresh()
print("Done.")

time.sleep(display.time_to_refresh + 5)

while True:
    time.sleep(10)
