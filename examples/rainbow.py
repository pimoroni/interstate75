import time
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128

i75 = Interstate75(DISPLAY_INTERSTATE75_128X128)
graphics = i75.display

WIDTH = i75.width
HEIGHT = i75.height
STRIPES = 0.5


@micropython.native  # noqa: F821
def draw(offset):
    for x in range(WIDTH):
        graphics.set_pen(graphics.create_pen_hsv(x / WIDTH * STRIPES + offset, 1.0, 0.5))
        graphics.line(x, 0, x, HEIGHT)

    i75.update(graphics)


t_total = 0
t_frames = 0

while True:
    t_start = time.ticks_ms()
    draw(time.ticks_ms() / 4000)
    t_total += time.ticks_diff(time.ticks_ms(), t_start)
    t_frames += 1

    if t_frames == 100:
        per_frame_avg = t_total / t_frames
        print(f"100 frames in {t_total}ms, avg {per_frame_avg:.02f}ms per frame, {1000 / per_frame_avg:.02f} FPS")
        t_frames = 0
        t_total = 0
