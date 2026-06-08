# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""4-gray "ThinkInk" info card for the Adafruit 2.13" SSD1680 eInk FeatherWing (#4195).

Confirmed on hardware 2026-06-05 (four distinct shades). Library path
(adafruit_ssd1680.SSD1680) — NO driver changes needed. 250x122 GDEY0213B74, FPC-A002.
rotation=270, vcom=0x24, custom_lut=FPC_A005_LUT, grayscale=True, colstart=0.

This is the FeatherWing sibling of ssd1680_2.13_grayscale.py (the #4197 breakout). The
panel film is the same GDEY0213B74, but #4195 ships the A-series FPC (FPC-A002), so it uses
FPC_A005_LUT (the 0x60 waveform), not the 75xx FPC7519_LUT used by the #4197 breakout.

FeatherWing wiring / gotchas:
  CS=D9  DC=D10   SCK/MOSI on the shared bus.
  BUSY is not connected on the Wing -> busy_pin=None (timed refresh).
  RST is on the Feather RESET line, not a GPIO -> FourWire reset=None. This is REQUIRED:
    with a reset pin the library issues a deep-sleep stop sequence, but SSD1680 deep sleep
    can only be exited by a hardware reset (which this Wing has no GPIO for), so the panel
    would stay asleep and every later refresh would show full-panel speckle. reset=None
    makes the library use an empty stop sequence (no deep sleep) -> panel stays awake.
  The A-series panel does not route SDO->MISO on this Wing, so panel auto-detection is not
  reliable here; the FPC_A005_LUT is selected explicitly.
"""

import time

import board
import displayio
import supervisor
import terminalio
from adafruit_display_text import label
from fourwire import FourWire

import adafruit_ssd1680

# Don't paint CircuitPython's status bar ("Done | x.y.z") onto the e-ink.
supervisor.status_bar.display = False

displayio.release_displays()

spi = board.SPI()
display_bus = FourWire(
    spi,
    command=board.D10,  # DC
    chip_select=board.D9,  # EPD CS
    reset=None,  # RST is on the Feather RESET line on this Wing -> no deep sleep
    baudrate=1000000,
)
time.sleep(1)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=250,
    height=122,
    rotation=270,
    colstart=0,
    vcom=0x24,
    custom_lut=adafruit_ssd1680.FPC_A005_LUT,  # FPC-A002 is the A-series -> 0x60 waveform
    grayscale=True,
    busy_pin=None,  # BUSY not connected on the Wing
    seconds_per_frame=5.0,
    refresh_time=2.0,
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
g.append(label.Label(terminalio.FONT, text="4-Gray FeatherWing", color=DARK, scale=2, x=6, y=64))
g.append(label.Label(terminalio.FONT, text="SSD1680  #4195", color=BLACK, scale=1, x=6, y=88))
display.root_group = g

print("Refreshing...")
display.refresh()
print("Done.")

time.sleep(display.time_to_refresh + 5)
print("Ready.")

while True:
    time.sleep(10)
