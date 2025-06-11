import gc
import time
import random
from ulab import numpy
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
from picographics import PEN_P8

i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128, pen_type=PEN_P8)
graphics = i75.display

width = i75.width
height = i75.height

"""
HELLO NEO.
"""

# MAXIMUM OVERKILL
# machine.freq(250_000_000)

# Fill half the palette with GREEEN
for g in range(128):
    _ = graphics.create_pen(0, g, 0)

# And half with bright green for white sparkles
for g in range(128):
    _ = graphics.create_pen(128, 128 + g, 128)


def update():

    for _ in range(4):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 11)
        m = random.randint(30, 127)
        for oy in range(10):
            matrix[y + oy][x] = random.randint(0, m) / 255.0
        matrix[y + 10][x] = random.randint(128, 255) / 255.0

    # Propagate downwards
    old = numpy.ndarray(matrix)
    matrix[:] = numpy.roll(matrix, 1, axis=0)
    matrix[:] *= 0.59
    matrix[:] += old * 0.39


def draw():
    # Copy the effect to the framebuffer
    memoryview(graphics)[:] = numpy.ndarray(numpy.clip(matrix, 0, 1) * 254, dtype=numpy.uint8).tobytes()



matrix = numpy.zeros((height, width))

t_count = 0
t_total = 0


while True:
    tstart = time.ticks_ms()
    gc.collect()
    update()
    draw()
    i75.update()
    tfinish = time.ticks_ms()

    total = tfinish - tstart
    t_total += total
    t_count += 1

    if t_count == 60:
        per_frame_avg = t_total / t_count
        print(f"60 frames in {t_total}ms, avg {per_frame_avg:.02f}ms per frame, {1000/per_frame_avg:.02f} FPS")
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
