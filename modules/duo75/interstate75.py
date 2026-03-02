from pimoroni import Button
from picographics import PicoGraphics, PEN_RGB888, DISPLAY_INTERSTATE75_32X32, DISPLAY_INTERSTATE75_64X32, DISPLAY_INTERSTATE75_96X32, DISPLAY_INTERSTATE75_96X48, DISPLAY_INTERSTATE75_128X32, DISPLAY_INTERSTATE75_64X64, DISPLAY_INTERSTATE75_128X64, DISPLAY_INTERSTATE75_192X64, DISPLAY_INTERSTATE75_256X64, DISPLAY_INTERSTATE75_128X128
import duo75
import machine
import neopixel

# Index Constants
SWITCH_A = 0
SWITCH_B = 1
SWITCH_C = 1
SWITCH_BOOT = 3
SWITCH_USER = 3


class Interstate75:
    SWITCH_PINS = ("SW_A", "SW_B", "SW_C", "SW_USER")

    # Display Types
    DISPLAY_INTERSTATE75_32X32 = DISPLAY_INTERSTATE75_32X32
    DISPLAY_INTERSTATE75_64X32 = DISPLAY_INTERSTATE75_64X32
    DISPLAY_INTERSTATE75_96X32 = DISPLAY_INTERSTATE75_96X32
    DISPLAY_INTERSTATE75_96X48 = DISPLAY_INTERSTATE75_96X48
    DISPLAY_INTERSTATE75_128X32 = DISPLAY_INTERSTATE75_128X32
    DISPLAY_INTERSTATE75_64X64 = DISPLAY_INTERSTATE75_64X64
    DISPLAY_INTERSTATE75_128X64 = DISPLAY_INTERSTATE75_128X64
    DISPLAY_INTERSTATE75_192X64 = DISPLAY_INTERSTATE75_192X64
    DISPLAY_INTERSTATE75_256X64 = DISPLAY_INTERSTATE75_256X64
    DISPLAY_INTERSTATE75_128X128 = DISPLAY_INTERSTATE75_128X128
    DISPLAY_INTERSTATE75_DUO = DISPLAY_INTERSTATE75_128X128

    # By setting these to None they'll just be quietly ignored if specified
    PANEL_GENERIC = None
    PANEL_FM6126A = None
    COLOR_ORDER_RGB = None
    COLOR_ORDER_RBG = None
    COLOR_ORDER_GRB = None
    COLOR_ORDER_GBR = None
    COLOR_ORDER_BRG = None
    COLOR_ORDER_BGR = None

    def __init__(self, display=None, panel_type=None, stb_invert=False, color_order=None, pen_type=PEN_RGB888):
        if display != DISPLAY_INTERSTATE75_128X128:
            raise ValueError("Unsupported display type for Duo.")

        if panel_type or stb_invert or color_order:
            raise ValueError("panel_type, stb_invert and color_order unsupported on Duo.")

        self.display = PicoGraphics(display=DISPLAY_INTERSTATE75_128X128, pen_type=pen_type)
        self.width, self.height = self.display.get_bounds()

        self.duo75 = duo75.Duo75()
        self.duo75.start()

        # We want people to use `Button("SW_A")` directly, really, but for
        # backwards compatibility add all the switch guff here
        self._switch_pins = self.SWITCH_PINS

        # Set up the user switches
        self.__switches = [Button(pin) for pin in self._switch_pins]

        # Interstate 75 Duo has a chain of four RGB LEDs
        # We don't want to use a PIO for these, so use MicroPython's bitbang PIO driver
        self._rgb = neopixel.NeoPixel(machine.Pin("LEDS"), 4, timing=1)

        # Set up the i2c for Qw/st and Breakout Garden
        self.i2c = machine.I2C()

    def set_blocking(self, blocking):
        self.duo75.set_blocking(blocking)

    def update(self, buffer=None):
        self.duo75.update(buffer or self.display)

    def is_busy(self):
        return self.duo75.is_busy()

    def wait_for_flip(self):
        while self.is_busy():
            pass

    def switch_pressed(self, switch):
        try:
            return self.__switches[switch].is_pressed
        except IndexError as err:
            raise ValueError("switch out of range. Expected SWITCH_A/B/C (0, 1, 2), or SWITCH_USER (3)") from err

    def set_led(self, r, g, b, index=None):
        if index is None:
            self._rgb.fill((r, g, b))
        else:
            self._rgb[index] = (r, g, b)
        self._rgb.write()
