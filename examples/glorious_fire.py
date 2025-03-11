import time
import gc
import random
import machine
import micropython
from ulab import numpy


from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128, stb_invert=False, panel_type=Interstate75.PANEL_FM6126A)
graphics = i75.display

"""
Classic fire effect.
Play with the number of spawns, heat, damping factor and colour palette to tweak it.
"""

# MEDIUM SPICY
machine.freq(200_000_000)

# MAXIMUM OVERKILL
# machine.freq(250_000_000)

# Size of an individual fire "pixel", bigger pixels = faster
SCALE = 3  # ideal values 2, 4, 8

# Number of random fire spawns
FIRE_SPAWNS = 16 // SCALE

# Fire damping
DAMPING_FACTOR = 0.99

# TURN UP THE HEEEAAT
HEAT = 3.0

# Original Colours
PALETTE = [
    graphics.create_pen(0, 0, 0),
    graphics.create_pen(5, 5, 5),
    graphics.create_pen(20, 20, 20),
    graphics.create_pen(180, 30, 0),
    graphics.create_pen(220, 160, 0),
    graphics.create_pen(255, 255, 180)
]

WHITE = graphics.create_pen(255, 255, 255)

PALETTE_SIZE = len(PALETTE)


@micropython.native
def update():
    global new

    # Clear the bottom two rows (off screen)
    heat[height - 1][:] = 0.0
    heat[height - 2][:] = 0.0

    # Add random fire spawns
    for c in range(FIRE_SPAWNS):
        x = random.randint(0, width - 4) + 2
        heat[height - 1][x - 1:x + 1] = HEAT / 2.0
        heat[height - 2][x - 1:x + 1] = HEAT

    # Copy the fire into a temporary bfufer so we can
    # do our rolls one at a time (not enough RAM for simultaneous)
    new[:] = heat

    # Propagate the fire upwards
    new += numpy.roll(heat, -1, axis=0)  # y + 1, x
    new += numpy.roll(heat, -2, axis=0)  # y + 2, x
    temp = numpy.roll(heat, -1, axis=0)  # y + 1
    new += numpy.roll(temp, 1, axis=1)      # y + 1, x + 1
    new += numpy.roll(temp, -1, axis=1)     # y + 1, x - 1

    # Average over 5 adjacent pixels and apply damping
    new *= DAMPING_FACTOR / 5.0
    heat[:] = new


pixels = bytearray(i75.width * i75.height)


@micropython.native
def draw():
    P = PALETTE
    pixels[:] = numpy.ndarray(numpy.clip(heat[0:(128 // SCALE), 0:(128 // SCALE)], 0, 1) * (PALETTE_SIZE - 1), dtype=numpy.uint8).tobytes()
    for y in range(height - 2):
        yw = y * width
        for x in range(width):
            graphics.set_pen(P[pixels[yw + x]])
            graphics.rectangle(x * SCALE + offset_x, y * SCALE + offset_y, SCALE, SCALE)
    graphics.set_pen(WHITE)
    graphics.text("This is\nfine!", 10, 10)
    i75.update(graphics)


width = i75.width // SCALE
height = (i75.height // SCALE) + 2
heat = numpy.zeros((height, width))
new = numpy.zeros((height, width))
offset_x = (i75.width % SCALE) // 2
offset_y = i75.width % SCALE

t_count = 0
t_total = 0

while True:
    tstart = time.ticks_ms()
    gc.collect()
    update()
    draw()
    tfinish = time.ticks_ms()

    total = tfinish - tstart
    t_total += total
    t_count += 1

    if t_count == 60:
        per_frame_avg = t_total / t_count
        print(f"60 frames in {t_total}ms, avg {per_frame_avg:.02f}ms per frame, {1000 / per_frame_avg:.02f} FPS")
        t_count = 0
        t_total = 0

    # pause for a moment (important or the USB serial device will fail)
    # try to pace at 60fps or 30fps
    if total > 1000 / 30:
        time.sleep(0.0001)
    elif total > 1000 / 60:
        t = 1000 / 30 - total
        time.sleep(t / 1000)
    else:
        t = 1000 / 60 - total
        time.sleep(t / 1000)
