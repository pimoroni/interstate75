import time
import random
import machine
import micropython
from micropython import const
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_256X64

# medium spicy overclock
machine.freq(200000000)

# uncomment for maximum speed
# machine.freq(266000000)

# Setup for the display
i75 = Interstate75(
    display=DISPLAY_INTERSTATE75_256X64, stb_invert=False, panel_type=Interstate75.PANEL_GENERIC)
graphics = i75.display

# These need to be constants for the viper optimized block below.
WIDTH = const(256 + 2)
HEIGHT = const(64 + 4)
fire_spawns = const(23)
damping_factor = const(807)  # int(0.98 * (1 << 12) // 5)

fire_colours = [graphics.create_pen(0, 0, 0),
                graphics.create_pen(20, 20, 20),
                graphics.create_pen(180, 30, 0),
                graphics.create_pen(220, 160, 0),
                graphics.create_pen(255, 255, 180)]

heat_array = bytearray(HEIGHT * WIDTH * 4)


@micropython.viper
def make_heat() -> ptr32:  # noqa: F821
    heat = ptr32(heat_array)  # noqa: F821
    return heat


@micropython.viper
def update(heat: ptr32):  # noqa: F821
    # clear the bottom row and then add a new fire seed to it
    for x in range(WIDTH):
        heat[x + WIDTH * (HEIGHT - 1)] = 0
        heat[x + WIDTH * (HEIGHT - 2)] = 0

    for c in range(fire_spawns):
        x = int(random.randint(2, WIDTH - 3))
        heat[x + 0 + WIDTH * (HEIGHT - 1)] += 65536
        heat[x + 1 + WIDTH * (HEIGHT - 1)] += 65536
        heat[x - 1 + WIDTH * (HEIGHT - 1)] += 65536
        heat[x + 0 + WIDTH * (HEIGHT - 2)] += 65536
        heat[x + 1 + WIDTH * (HEIGHT - 2)] += 65536
        heat[x - 1 + WIDTH * (HEIGHT - 2)] += 65536

    # Propagate the fire using fixed point arithmetic
    for y in range(0, HEIGHT - 2):
        for x in range(1, WIDTH - 1):
            new_heat = heat[x + WIDTH * y] + heat[x + WIDTH * (y + 1)] + heat[x + WIDTH * (y + 2)] + heat[x - 1 + WIDTH * (y + 1)] + heat[x + 1 + WIDTH * (y + 1)]
            new_heat *= damping_factor
            heat[x + WIDTH * y] = new_heat >> 12


@micropython.viper
def draw(heat: ptr32, graphics: ptr32):  # noqa: F821
    # Convert the fixed point heat values into RGB888 colours,
    # writing directly to the graphics buffer
    for y in range(HEIGHT - 4):
        for x in range(WIDTH - 2):
            value = heat[x + 1 + y * WIDTH]
            if value < 9830:
                colour = 0
            elif value < 16384:
                colour = 0x141414
            elif value < 22938:
                colour = 0xb41e00
            elif value < 29490:
                colour = 0xdca000
            else:
                colour = 0xffffb4
            graphics[x + 256 * y] = colour

    i75.update()


heat = make_heat()

while True:
    start = time.ticks_ms()

    update(heat)
    draw(heat, memoryview(graphics))

    print("total took: {} ms".format(time.ticks_ms() - start))

    # pause for a moment (important or the USB serial device will fail)
    time.sleep(0.001)
