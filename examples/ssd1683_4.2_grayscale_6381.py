# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""4-gray grayscale info card for the Adafruit 4.2" 400x300 E-Ink Display (#6381).

displayio / SSD1683 driver. Layout mirrors the adafruit_epd PR #111 example:
big built-in font (scale 3-4) and a tall 4-box gray ramp that fills the panel.
FPC-190 ribbon. Tested on Adafruit Feather RP2040 ThinkInk.
"""

import time

import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
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
    rotation=0,
    colstart=0,
    vcom=0x30,
    custom_lut=adafruit_ssd1680.SSD1683_GRAY4_LUT,
)

W, H = 400, 300

# 4-gray palette (white -> black)
pal = displayio.Palette(4)
pal[0] = 0xFFFFFF  # white
pal[1] = 0xAAAAAA  # light gray
pal[2] = 0x555555  # dark gray
pal[3] = 0x000000  # black
WHITE, LIGHT, DARK, BLACK = 0, 1, 2, 3

g = displayio.Group()

# White background
bg = displayio.Bitmap(W, H, 4)
bg.fill(WHITE)
g.append(displayio.TileGrid(bg, pixel_shader=pal))

# Big text, sized to fill the 400px width (matches PR #111: scale 3-4)
texts = [
    ("Adafruit ThinkInk", 6, 10, 3, 0x000000),
    ('4.2" 400x300', 6, 50, 4, 0x000000),
    ("4-Gray E-Ink", 6, 95, 4, 0x555555),
    ("SSD1683  #6381", 6, 140, 3, 0x000000),
]
for text, x, y, scale, color in texts:
    lbl = label.Label(terminalio.FONT, text=text, color=color, scale=scale)
    lbl.anchor_point = (0.0, 0.0)  # top-left, like framebuf text()
    lbl.anchored_position = (x, y)
    g.append(lbl)

# 4-level gray ramp filling the bottom: black | dark | light | white, with borders
RAMP_TOP = 180
RAMP_H = H - RAMP_TOP
SEG = W // 4
order = (BLACK, DARK, LIGHT, WHITE)  # left -> right
ramp = displayio.Bitmap(W, RAMP_H, 4)
for x in range(W):
    col = order[min(x // SEG, 3)]
    for y in range(RAMP_H):
        ramp[x, y] = col
# black outline + dividers
for x in range(W):
    ramp[x, 0] = BLACK
    ramp[x, RAMP_H - 1] = BLACK
for y in range(RAMP_H):
    ramp[0, y] = BLACK
    ramp[W - 1, y] = BLACK
    for i in range(1, 4):
        ramp[i * SEG, y] = BLACK
g.append(displayio.TileGrid(ramp, pixel_shader=pal, x=0, y=RAMP_TOP))

display.root_group = g
print("Refreshing 4-gray info card...")
display.refresh()
print("Done.")

time.sleep(display.time_to_refresh + 5)
while True:
    time.sleep(10)
