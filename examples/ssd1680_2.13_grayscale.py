# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""4-gray "ThinkInk" info card for the Adafruit 2.13" SSD1680 Breakout (#4197).

A grayscale take on the factory demo: product text plus a 4-level gray ramp
(white / light / dark / black) that shows all four shades at once.

Wiring — Feather + EYESPI Breakout to the #4197 EYESPI connector:
  TCS  -> D9   (use the TCS pad, not ECS/SDCS/TSCS)
  DC   -> D10
  RST  -> D11
  BUSY -> D12
  SCK  -> SCK   MOSI -> MOSI   3V3 -> 3V3   GND -> GND
"""

import time

import board
import displayio
import terminalio
from adafruit_display_text import label
from fourwire import FourWire

import adafruit_ssd1680

displayio.release_displays()

spi = board.SPI()
display_bus = FourWire(
    spi,
    command=board.D10,  # DC
    chip_select=board.D9,  # TCS on EYESPI breakout
    reset=board.D11,
    baudrate=1000000,
)
time.sleep(1)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=250,
    height=122,
    busy_pin=board.D12,
    rotation=270,
    colstart=0,
    vcom=0x1C,
    custom_lut=adafruit_ssd1680.FPC7519_LUT,
    grayscale=True,
)

WHITE = 0xFFFFFF
LIGHT = 0xAAAAAA
DARK = 0x555555
BLACK = 0x000000
W, H = 250, 122

# White background + a 4-level gray ramp across the bottom
bg = displayio.Bitmap(W, H, 4)
pal = displayio.Palette(4)
pal[0], pal[1], pal[2], pal[3] = WHITE, LIGHT, DARK, BLACK  # indices 0..3

ramp_top, ramp_bot = 100, 120
seg = W // 4
for x in range(W):
    level = 3 - min(x // seg, 3)  # left=black(3) .. right=white(0)
    for y in range(ramp_top, ramp_bot):
        bg[x, y] = level
# 1px black border + dividers so every block (incl. white) reads distinctly
for x in range(W):
    bg[x, ramp_top] = 3
    bg[x, ramp_bot - 1] = 3
for y in range(ramp_top, ramp_bot):
    bg[0, y] = 3
    bg[W - 1, y] = 3
for i in range(1, 4):
    for y in range(ramp_top, ramp_bot):
        bg[i * seg, y] = 3

g = displayio.Group()
g.append(displayio.TileGrid(bg, pixel_shader=pal))
g.append(label.Label(terminalio.FONT, text="Adafruit ThinkInk", color=BLACK, scale=2, x=6, y=14))
g.append(label.Label(terminalio.FONT, text='2.13" 250x122', color=BLACK, scale=2, x=6, y=40))
g.append(label.Label(terminalio.FONT, text="4-Gray E-Ink", color=DARK, scale=2, x=6, y=64))
g.append(label.Label(terminalio.FONT, text="SSD1680 Driver", color=BLACK, scale=1, x=6, y=88))
display.root_group = g

print("Refreshing...")
display.refresh()
print("Done.")

time.sleep(display.time_to_refresh + 5)
print("Ready.")

while True:
    time.sleep(10)
