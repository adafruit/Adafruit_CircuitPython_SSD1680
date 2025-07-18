# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_ssd1680`
================================================================================

CircuitPython `displayio` driver for SSD1680-based ePaper displays


* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Hardware:**

* `Adafruit 2.13" Tri-Color eInk Display Breakout <https://www.adafruit.com/product/4947>`_
* `Adafruit 2.13" Tri-Color eInk Display FeatherWing <https://www.adafruit.com/product/4814>`_
* `Adafruit 2.13" Mono eInk Display FeatherWing <https://www.adafruit.com/product/4195>`_


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

from epaperdisplay import EPaperDisplay

try:
    import typing

    from fourwire import FourWire
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SSD1680.git"

_START_SEQUENCE = (
    b"\x12\x80\x00\x14"  # soft reset and wait 20ms
    b"\x11\x00\x01\x03"  # Ram data entry mode
    b"\x3c\x00\x01\x03"  # border color
    b"\x2c\x00\x01\x36"  # Set vcom voltage
    b"\x03\x00\x01\x17"  # Set gate voltage
    b"\x04\x00\x03\x41\xae\x32"  # Set source voltage
    b"\x4e\x00\x01\x01"  # ram x count
    b"\x4f\x00\x02\x00\x00"  # ram y count
    b"\x01\x00\x03\x00\x00\x00"  # set display size
)

_DISPLAY_UPDATE_MODE = (
    b"\x22\x00\x01\xf4"  # display update mode
)

_STOP_SEQUENCE = b"\x10\x80\x01\x01\x64"  # Deep Sleep


# pylint: disable=too-few-public-methods
class SSD1680(EPaperDisplay):
    r"""SSD1680 driver

    :param bus: The data bus the display is on
    :param \**kwargs:
        See below

    :Keyword Arguments:
        * *width* (``int``) --
          Display width
        * *height* (``int``) --
          Display height
        * *rotation* (``int``) --
          Display rotation
        * *vcom* (``int``) --
          Set vcom voltage register value
        * *vsh2* (``int``) --
          Set vsh2 voltage register value
        * *custom_lut* (``bytes``) --
          Custom look-up table settings
    """

    def __init__(self, bus: FourWire, vcom:int = 0x36, vsh2:int = 0x00, custom_lut: bytes = b"", **kwargs) -> None:
        if "colstart" not in kwargs:
            kwargs["colstart"] = 8
        stop_sequence = bytearray(_STOP_SEQUENCE)
        try:
            bus.reset()
        except RuntimeError:
            # No reset pin defined, so no deep sleeping
            stop_sequence = b""
        load_lut = b""
        display_update_mode = bytearray(_DISPLAY_UPDATE_MODE)
        if custom_lut:
            load_lut = b"\x32" + len(custom_lut).to_bytes(2) + custom_lut
            display_update_mode[-1] = 0xc7

        start_sequence = bytearray(_START_SEQUENCE + load_lut + display_update_mode)
        start_sequence[15] = vcom

        start_sequence[24] = vsh2

        width = kwargs["width"]
        height = kwargs["height"]
        if "rotation" in kwargs and kwargs["rotation"] % 180 != 90:
            width, height = height, width
        start_sequence[38] = (width - 1) & 0xFF
        start_sequence[39] = ((width - 1) >> 8) & 0xFF

        super().__init__(
            bus,
            start_sequence,
            stop_sequence,
            **kwargs,
            ram_width=250,
            ram_height=296,
            busy_state=True,
            write_black_ram_command=0x24,
            write_color_ram_command=0x26,
            set_column_window_command=0x44,
            set_row_window_command=0x45,
            set_current_column_command=0x4E,
            set_current_row_command=0x4F,
            refresh_display_command=0x20,
            always_toggle_chip_select=False,
            address_little_endian=True,
            two_byte_sequence_length=True
        )
