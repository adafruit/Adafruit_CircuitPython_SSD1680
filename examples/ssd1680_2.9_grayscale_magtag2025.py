# SPDX-FileCopyrightText: 2025 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Simple test script for 2.9" 296x128 display. This example runs it in 2bit grayscale mode.

Automatically detects whether the MagTag has the original FPC-A005 panel or the
newer FPC-7519rev.b panel by reading SSD1680 User ID register 0x2E via half-duplex
bitbang SPI (the same method used by CircuitPython's built-in MagTag board support).
"""

import time

import board
import busio
import digitalio
import displayio
from fourwire import FourWire

import adafruit_ssd1680

# LUT for original MagTag panel: FPC-A005 (SSD1680, User ID first byte 0x00)
_FPC_A005_LUT = (
    b"\x2a\x60\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L0
    b"\x20\x60\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L1
    b"\x28\x60\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L2
    b"\x00\x60\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L3
    b"\x00\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L4
    b"\x00\x02\x00\x05\x14\x00\x00"  # TP, SR, RP Group0
    b"\x1e\x1e\x00\x00\x00\x00\x01"  # TP, SR, RP Group1
    b"\x00\x02\x00\x05\x14\x00\x00"  # TP, SR, RP Group2
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group3
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group4
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group5
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group6
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group7
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group8
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group9
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group10
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group11
    b"\x24\x22\x22\x22\x23\x32\x00\x00\x00"  # FR, XON
)

# LUT for newer MagTag panel: FPC-7519rev.b (SSD1680, User ID first byte 0x44 or 0xca).
# GxEPD2_4G (GDEM029T94) waveform with L0/L3 swapped to match CircuitPython's luma mapping
# (luma 0→L0=black, luma 255→L3=white) and 0x48 flag for DC-balanced drive.
_FPC7519_LUT = (
    b"\x20\x48\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L0 (black)
    b"\x08\x48\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L1 (dark gray)
    b"\x02\x48\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L2 (light gray)
    b"\x40\x48\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L3 (white)
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # VS L4 (VCOM)
    b"\x0a\x19\x00\x03\x08\x00\x00"  # TP, SR, RP Group0
    b"\x14\x01\x00\x14\x01\x00\x03"  # TP, SR, RP Group1
    b"\x0a\x03\x00\x08\x19\x00\x00"  # TP, SR, RP Group2
    b"\x01\x00\x00\x00\x00\x00\x01"  # TP, SR, RP Group3
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group4
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group5
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group6
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group7
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group8
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group9
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group10
    b"\x00\x00\x00\x00\x00\x00\x00"  # TP, SR, RP Group11
    b"\x22\x22\x22\x22\x22\x22\x00\x00\x00"  # FR, XON
)


def detect_ssd1680_panel():
    """Read SSD1680 User ID (register 0x2E) via half-duplex bitbang SPI.

    The SSD1680 responds on the MOSI/DATA line in half-duplex mode, not MISO.
    This mirrors the detection used by CircuitPython's built-in MagTag support.

    Returns first byte of User ID:
      0x00        -> FPC-A005 (original MagTag panel)
      0x44, 0xca  -> FPC-7519rev.b (newer MagTag panel)
      0xff        -> IL0373 (not an SSD1680)
    """
    data = digitalio.DigitalInOut(board.EPD_MOSI)
    clk = digitalio.DigitalInOut(board.EPD_SCK)
    cs = digitalio.DigitalInOut(board.EPD_CS)
    dc = digitalio.DigitalInOut(board.EPD_DC)
    rst = digitalio.DigitalInOut(board.EPD_RESET)

    for pin in (data, clk, cs, dc, rst):
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = False

    # Hardware reset to exit SSD1680 deep sleep (entered by the stop sequence)
    rst.value = False
    time.sleep(0.001)
    rst.value = True
    time.sleep(0.010)

    # Send command byte 0x2E with CS and DC both low (command phase)
    cmd = 0x2E
    for i in range(8):
        data.value = bool(cmd & (1 << (7 - i)))
        clk.value = True
        clk.value = False

    # Switch DATA to input with pull-up; raise DC for data-read phase
    data.switch_to_input(pull=digitalio.Pull.UP)
    dc.value = True

    result = 0
    for _ in range(8):
        result = (result << 1) | (1 if data.value else 0)
        clk.value = True
        clk.value = False

    cs.value = True

    for pin in (data, clk, cs, dc, rst):
        pin.deinit()

    return result


displayio.release_displays()

panel_id = detect_ssd1680_panel()
print(f"SSD1680 User ID first byte: 0x{panel_id:02x}")

if panel_id in (0x44, 0xCA):
    print("Detected: FPC-7519rev.b panel")
    vcom = 0x24
    colstart = 8
    lut = _FPC7519_LUT
else:
    print("Detected: FPC-A005 panel (or unknown, using defaults)")
    vcom = 0x28
    colstart = 0
    lut = _FPC_A005_LUT

# This pinout works on a MagTag and may need to be altered for other boards.
spi = busio.SPI(board.EPD_SCK, board.EPD_MOSI)
epd_cs = board.EPD_CS
epd_dc = board.EPD_DC
epd_reset = board.EPD_RESET
epd_busy = board.EPD_BUSY

display_bus = FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
time.sleep(1)

assert len(lut) == 153, f"LUT must be 153 bytes, got {len(lut)}"

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=296,
    height=128,
    busy_pin=epd_busy,
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
# Always refresh a little longer. It's not a problem to refresh
# a few seconds more, but it's terrible to refresh too early
# (the display will throw an exception when if the refresh
# is too soon)
print("waited correct time")


# Keep the display the same
while True:
    time.sleep(10)
