from pimoroni import Button
from picographics import PicoGraphics, PEN_RGB888, DISPLAY_INTERSTATE75_32X32, DISPLAY_INTERSTATE75_64X32, DISPLAY_INTERSTATE75_96X32, DISPLAY_INTERSTATE75_96X48, DISPLAY_INTERSTATE75_128X32, DISPLAY_INTERSTATE75_64X64, DISPLAY_INTERSTATE75_128X64, DISPLAY_INTERSTATE75_192X64, DISPLAY_INTERSTATE75_256X64, DISPLAY_INTERSTATE75_128X128
from pimoroni_i2c import PimoroniI2C
import hub75
import plasma

# Index Constants
SWITCH_A = 0
SWITCH_B = 1
SWITCH_BOOT = 2


class Interstate75:
    I2C_SDA_PIN = 20
    I2C_SCL_PIN = 21
    SWITCH_PINS = (14, 15, 22)
    WS2812_PIN = 18  # For Interstate 75 W (RP2350)

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

    PANEL_GENERIC = hub75.PANEL_GENERIC
    PANEL_FM6126A = hub75.PANEL_FM6126A
    COLOR_ORDER_RGB = hub75.COLOR_ORDER_RGB
    COLOR_ORDER_RBG = hub75.COLOR_ORDER_RBG
    COLOR_ORDER_GRB = hub75.COLOR_ORDER_GRB
    COLOR_ORDER_GBR = hub75.COLOR_ORDER_GBR
    COLOR_ORDER_BRG = hub75.COLOR_ORDER_BRG
    COLOR_ORDER_BGR = hub75.COLOR_ORDER_BGR

    # Count Constants
    NUM_SWITCHES = 3

    def __init__(self, display, panel_type=hub75.PANEL_GENERIC, stb_invert=False, color_order=hub75.COLOR_ORDER_RGB, pen_type=PEN_RGB888):
        self.display = PicoGraphics(display=display, pen_type=pen_type)
        self.width, self.height = self.display.get_bounds()

        out_width = self.width
        out_height = self.height

        if display == DISPLAY_INTERSTATE75_128X128:
            out_width = 256
            out_height = 64

        self.hub75 = hub75.Hub75(out_width, out_height, panel_type=panel_type, stb_invert=stb_invert, color_order=color_order)
        self.hub75.start()
        self._switch_pins = self.SWITCH_PINS

        # Set up the user switches
        self.__switches = []
        for i in range(self.NUM_SWITCHES):
            self.__switches.append(Button(self._switch_pins[i]))

        # The RGB LED is a WS2812 on Interstate 75 W (RP2350)
        self.__rgb = plasma.WS2812(1, 0, 2, Interstate75.WS2812_PIN)
        self.__rgb.start()

        # Set up the i2c for Qw/st and Breakout Garden
        self.i2c = PimoroniI2C(self.I2C_SDA_PIN, self.I2C_SCL_PIN, 100000)

    def update(self, buffer=None):
        if buffer is None:
            buffer = self.display
        self.hub75.update(buffer)

    def switch_pressed(self, switch):
        if switch < 0 or switch >= self.NUM_SWITCHES:
            raise ValueError("switch out of range. Expected SWITCH_A (0), SWITCH_B/BOOT (2)")
        return self.__switches[switch].is_pressed

    def set_led(self, r, g, b):
        self.__rgb.set_rgb(0, r, g, b)
