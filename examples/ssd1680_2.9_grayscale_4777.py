# SPDX-FileCopyrightText: 2026 Mikey Sklar, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""4-gray "ThinkInk" info card for the Adafruit 2.9" SSD1680 eInk FeatherWing (#4777).

Confirmed on hardware 2026-06-04. Library path (adafruit_ssd1680.SSD1680) — NO driver
changes needed (grayscale plumbing from PR #41 is already on main). 296x128 GDEM029T94,
FPC-7519rev.b. rotation=270, vcom=0x24, vsh2=0xAE, custom_lut=FPC7519_LUT, grayscale=True,
colstart=0 (this Wing — see note below; not the MagTag value of 8).

Autodetects the panel by reading the SSD1680 User ID register before the SPI bus is
initialized (readback works on this FeatherWing): 0x00 -> FPC-A005 legacy, else newer.

FeatherWing wiring notes:
  CS=D9  DC=D10  (RST used for detect only on D11)  SCK/MOSI on the shared bus.
  BUSY is not connected on the Wing  -> busy_pin=None (timed refresh).
  RST is on the Feather RESET line, not a GPIO -> FourWire reset=None (no deep sleep);
  run after a Feather hardware reset so the panel starts awake.
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

panel_id = adafruit_ssd1680.detect_ssd1680_panel(
    board.MOSI, board.SCK, board.D9, board.D10, board.D11
)
print(f"SSD1680 User ID first byte: 0x{panel_id:02x}")
if panel_id == 0x00:
    print("Detected: FPC-A005 panel (legacy)")
    vcom, lut = 0x28, adafruit_ssd1680.FPC_A005_LUT
else:
    print("Detected: FPC-7519rev.b or newer panel")
    vcom, lut = 0x24, adafruit_ssd1680.FPC7519_LUT

# colstart=0 on the #4777 FeatherWing: colstart=8 (the MagTag value for this same
# FPC-7519 panel) leaves RAM byte 0 unwritten -> an 8px black line on the top row.
# The Wing mounts the panel differently than the MagTag, so byte 0 must be written.
colstart = 0

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
    width=296,
    height=128,
    rotation=270,
    colstart=colstart,
    vcom=vcom,
    vsh2=0xAE,
    custom_lut=lut,
    grayscale=True,
    busy_pin=None,  # BUSY not connected on the Wing
    seconds_per_frame=5.0,
    refresh_time=2.0,
)

WHITE = 0xFFFFFF
LIGHT = 0xAAAAAA
DARK = 0x555555
BLACK = 0x000000
W, H = 296, 128

bg = displayio.Bitmap(W, H, 4)
pal = displayio.Palette(4)
pal[0], pal[1], pal[2], pal[3] = WHITE, LIGHT, DARK, BLACK

# 4-level gray ramp across the bottom
ramp_top, ramp_bot = H - 30, H - 6
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
g.append(label.Label(terminalio.FONT, text="Adafruit ThinkInk", color=BLACK, scale=2, x=8, y=18))
g.append(label.Label(terminalio.FONT, text='2.9" 296x128', color=BLACK, scale=2, x=8, y=46))
g.append(
    label.Label(terminalio.FONT, text="4-Gray  SSD1680  #4777", color=DARK, scale=1, x=8, y=74)
)
display.root_group = g

print("Refreshing...")
display.refresh()
print(f"Done — id=0x{panel_id:02x}, vcom=0x{vcom:02X}, colstart={colstart}")

while True:
    time.sleep(10)
