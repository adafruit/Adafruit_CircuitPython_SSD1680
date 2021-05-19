Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ssd1680/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/ssd1680/en/latest/
    :alt: Documentation Status


.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_SSD1680/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_SSD1680/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

CircuitPython `displayio` driver for SSD1680-based ePaper displays


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

* Adafruit 2.13" 250x122 Tri-Color eInk / ePaper Display with SRAM - SSD1680 Driver

`Purchase the Breakout from the Adafruit shop <http://www.adafruit.com/products/4947>`_

* Adafruit 2.13" HD Tri-Color eInk / ePaper Display FeatherWing - 250x122 RW Panel with SSD1680

`Purchase the FeatherWing from the Adafruit shop <http://www.adafruit.com/products/4814>`_

Usage Example
=============

.. code-block:: python

    import time
    import board
    import displayio
    import adafruit_ssd1680

    displayio.release_displays()

    # This pinout works on a Metro M4 and may need to be altered for other boards.
    spi = board.SPI()  # Uses SCK and MOSI
    epd_cs = board.D9
    epd_dc = board.D10
    epd_reset = board.D8    # Set to None for FeatherWing
    epd_busy = board.D7    # Set to None for FeatherWing

    display_bus = displayio.FourWire(
        spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
    )
    time.sleep(1)

    display = adafruit_ssd1680.SSD1680(
        display_bus,
        width=250,
        height=122,
        busy_pin=epd_busy,
        highlight_color=0xFF0000,
        rotation=270,
    )

    g = displayio.Group()

    f = open("/display-ruler.bmp", "rb")

    pic = displayio.OnDiskBitmap(f)
    t = displayio.TileGrid(pic, pixel_shader=displayio.ColorConverter())
    g.append(t)

    display.show(g)

    display.refresh()

    print("refreshed")

    time.sleep(120)


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_SSD1680/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.