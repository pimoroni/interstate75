import time
import re
import machine  # noqa: F401
import micropython
from micropython import const
from random import randint
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128

"""
Conway's Game Of Life for Interstate 75
You can load game of life RLE files below to try different patterns
See https://conwaylife.com/ref/DRH/ to find some RLE examples.
"""

# Runs ~20fps with stock clock,

# uncomment the below for ~30fps
# machine.freq(200_000_000)

# uncomment the below for ~40fps
# machine.freq(250_000_000)

# Vibrant yellow, trailing off to purple
PLASMA = b'\x00\x00\x00\x00\x11\x00\x02\x00#\x01\x06\x006\x02\x0b\x00I\x02\x11\x00K\x02\x13\x00L\x02\x15\x00M\x02\x17\x00N\x02\x19\x00P\x02\x1b\x00Q\x02\x1d\x00R\x02\x1f\x00S\x01!\x00T\x01#\x00V\x01%\x00W\x01\'\x00X\x01)\x00Y\x01+\x00Z\x00-\x00[\x00/\x00\\\x001\x00]\x004\x00^\x006\x00^\x008\x00_\x00:\x00`\x00<\x00a\x00>\x00a\x00@\x00b\x00B\x00b\x00D\x00c\x00G\x00c\x01I\x00d\x01K\x00d\x02M\x00d\x03O\x00d\x04Q\x00d\x05T\x00d\x06V\x00d\x08X\x00d\tZ\x00d\n\\\x00d\x0c_\x00d\ra\x00c\x0fc\x00c\x10e\x00b\x12g\x00b\x13j\x00a\x15l\x00a\x17n\x00`\x18p\x00_\x1ar\x00_\x1bt\x00^\x1dw\x00]\x1fy\x00] {\x00\\"}\x00[$\x7f\x00Z&\x81\x00Y\'\x83\x00Y)\x86\x00X+\x88\x00W-\x8a\x00V/\x8c\x00U0\x8e\x00T3\x91\x00S5\x93\x00R7\x95\x00Q9\x97\x00Q;\x99\x00P=\x9b\x00O?\x9d\x00NA\x9f\x00MC\xa2\x00LE\xa4\x00KG\xa6\x00JI\xa8\x00JK\xaa\x00IN\xac\x00HP\xae\x00GR\xb0\x00FT\xb2\x00EW\xb4\x00DY\xb6\x00C\\\xb8\x00B^\xba\x00Aa\xbc\x00@c\xbe\x00?f\xc0\x00>h\xc2\x00=k\xc4\x00<n\xc6\x00;p\xc8\x00:s\xca\x008v\xcc\x007y\xce\x006|\xd0\x005\x7f\xd2\x004\x82\xd3\x003\x85\xd5\x001\x88\xd7\x000\x8b\xd9\x00/\x8f\xda\x00.\x92\xdc\x00-\x95\xdd\x00+\x99\xdf\x00*\x9c\xe0\x00)\xa0\xe2\x00(\xa3\xe3\x00\'\xa7\xe4\x00&\xab\xe5\x00%\xaf\xe7\x00$\xb2\xe8\x00#\xb6\xe9\x00#\xba\xea\x00"\xbe\xeb\x00"\xc2\xeb\x00"\xc7\xec\x00"\xcb\xed\x00"\xcf\xed\x00#\xd3\xee\x00#\xd8\xee\x00$\xdc\xef\x00%\xe1\xef\x00%\xe5\xef\x00&\xea\xef\x00&\xef\xef\x00%\xf3\xef\x00!\xf8\xef\x00'

# Neutral toned with a trail off to blue
TWILIGHT = b'\x00\x00\x00\x00\x02\x02\x02\x00\x04\x04\x04\x00\x06\x06\x06\x00\t\x08\x08\x00\x0b\x0b\x0b\x00\r\r\r\x00\x0f\x0f\x0e\x00\x12\x11\x10\x00\x14\x13\x12\x00\x16\x15\x13\x00\x18\x17\x15\x00\x1a\x19\x16\x00\x1c\x1b\x17\x00\x1f\x1c\x18\x00!\x1e\x19\x00# \x1a\x00%!\x1b\x00\'#\x1b\x00*$\x1c\x00,%\x1d\x00.&\x1d\x001(\x1e\x003)\x1f\x005*\x1f\x008* \x00:+!\x00=,!\x00?,"\x00A-#\x00D-$\x00F-%\x00H-&\x00J-\'\x00L-(\x00N,)\x00P,*\x00R++\x00T*-\x00V).\x00W(/\x00X\'1\x00Y%2\x00Z$3\x00["5\x00[ 6\x00[\x1e7\x00[\x1c8\x00Z\x1a8\x00Y\x189\x00U\x158\x00R\x137\x00N\x115\x00J\x104\x00E\x0e2\x00A\r0\x00=\x0c.\x009\x0c,\x005\x0b*\x002\x0b(\x00/\x0b&\x00,\x0b%\x00*\x0c#\x00(\r"\x00&\r"\x00\'\x0c$\x00(\x0c&\x00)\x0c(\x00*\x0c+\x00,\x0c.\x00.\r2\x000\r5\x001\x0e9\x003\x0f=\x005\x10B\x007\x11F\x008\x12J\x00:\x13O\x00;\x14S\x00<\x16X\x00=\x18\\\x00>\x1aa\x00>\x1ce\x00?\x1ei\x00? m\x00?#q\x00?&u\x00@)y\x00@-}\x00@0\x81\x00A4\x84\x00A7\x88\x00B;\x8b\x00B?\x8e\x00CC\x91\x00DG\x95\x00FK\x98\x00GP\x9a\x00IT\x9d\x00KY\xa0\x00M]\xa3\x00Ob\xa5\x00Rg\xa8\x00Uk\xaa\x00Yp\xac\x00]u\xae\x00az\xb0\x00f\x80\xb2\x00k\x85\xb4\x00p\x8a\xb6\x00v\x8f\xb8\x00|\x94\xba\x00\x82\x99\xbc\x00\x89\x9f\xbf\x00\x90\xa4\xc1\x00\x97\xa9\xc3\x00\x9e\xae\xc6\x00\xa5\xb3\xc9\x00\xad\xb8\xcb\x00\xb4\xbd\xce\x00\xbc\xc2\xd1\x00\xc3\xc6\xd4\x00\xc9\xca\xd7\x00\xcf\xce\xd9\x00\xd5\xd2\xdb\x00\xd9\xd4\xde\x00\xde\xd7\xe0\x00\xe1\xd8\xe1\x00'

# Yellow/green with a trail off to blue
VIRIDIS = b'\x00\x00\x00\x00\n\x00\x08\x00\x16\x01\x11\x00#\x03\x1a\x001\x06$\x002\x08$\x004\t%\x006\x0b%\x007\x0c%\x009\x0e&\x00:\x0f&\x00<\x11&\x00=\x12&\x00?\x14&\x00@\x15&\x00B\x17&\x00C\x18&\x00D\x1a&\x00F\x1b&\x00G\x1d&\x00H\x1e&\x00I &\x00J!&\x00K#&\x00L$%\x00M&%\x00N\'%\x00O)$\x00P*$\x00P,$\x00Q-#\x00R/#\x00S1"\x00S2"\x00T4"\x00U5!\x00U7!\x00V8 \x00W: \x00W< \x00X=\x1f\x00X?\x1f\x00Y@\x1e\x00YB\x1e\x00ZD\x1e\x00[E\x1d\x00[G\x1d\x00\\H\x1d\x00\\J\x1c\x00]L\x1c\x00]M\x1b\x00^O\x1b\x00^Q\x1b\x00_R\x1a\x00_T\x1a\x00`V\x1a\x00`X\x19\x00aY\x19\x00a[\x19\x00a]\x18\x00b_\x18\x00ba\x18\x00cb\x17\x00cd\x17\x00cg\x16\x00ci\x16\x00dk\x16\x00dm\x16\x00do\x16\x00dq\x16\x00ds\x16\x00du\x16\x00dw\x16\x00dy\x17\x00d{\x18\x00d}\x19\x00d\x7f\x1a\x00c\x81\x1b\x00c\x83\x1c\x00c\x85\x1e\x00b\x87 \x00b\x89!\x00a\x8c$\x00`\x8e&\x00`\x90(\x00_\x92+\x00^\x94.\x00]\x961\x00\\\x994\x00[\x9b7\x00Z\x9d:\x00X\x9f>\x00W\xa1A\x00V\xa4E\x00T\xa6I\x00S\xa8M\x00Q\xaaQ\x00O\xacU\x00M\xaeY\x00K\xb1^\x00I\xb3b\x00G\xb5g\x00E\xb7l\x00C\xb9q\x00@\xbbv\x00>\xbd{\x00;\xbf\x80\x009\xc1\x85\x006\xc3\x8b\x003\xc5\x90\x000\xc7\x96\x00-\xc9\x9c\x00*\xcb\xa1\x00(\xcd\xa7\x00%\xcf\xad\x00"\xd1\xb3\x00\x1f\xd2\xb9\x00\x1c\xd4\xbf\x00\x1a\xd6\xc5\x00\x19\xd8\xcb\x00\x17\xda\xd2\x00\x17\xdb\xd8\x00\x17\xdd\xde\x00\x19\xdf\xe4\x00\x1b\xe1\xea\x00\x1d\xe3\xf0\x00!\xe5\xf7\x00$\xe7\xfd\x00'

# Heap map style
TURBO = b'\x00\x00\x00\x00\t\x03\x06\x00\x16\x07\r\x00&\r\x15\x00:\x15\x1d\x00A\x18\x1e\x00H\x1b\x1f\x00N\x1e \x00T!!\x00Z$"\x00`\'#\x00e+#\x00j.$\x00o1%\x00t4%\x00x7&\x00|:&\x00\x80=&\x00\x83A\'\x00\x86D\'\x00\x89G\'\x00\x8cJ\'\x00\x8eM\'\x00\x90Q&\x00\x91T%\x00\x92W$\x00\x92[#\x00\x92^!\x00\x91b\x1f\x00\x91e\x1d\x00\x8fi\x1c\x00\x8el\x1a\x00\x8cp\x18\x00\x8as\x16\x00\x88v\x14\x00\x86z\x12\x00\x83}\x11\x00\x80\x80\x10\x00~\x83\x0f\x00{\x86\x0e\x00y\x89\x0e\x00v\x8c\x0f\x00t\x8f\x10\x00r\x91\x11\x00o\x94\x13\x00l\x96\x16\x00i\x99\x19\x00f\x9b\x1c\x00b\x9d \x00_\x9f$\x00[\xa1)\x00W\xa3.\x00S\xa53\x00O\xa79\x00J\xa9>\x00F\xaaD\x00B\xacJ\x00?\xadO\x00;\xafU\x007\xb0[\x004\xb1`\x001\xb1f\x00.\xb2k\x00,\xb3p\x00)\xb2v\x00\'\xb2z\x00&\xb2\x7f\x00&\xb2\x83\x00%\xb1\x88\x00%\xb1\x8c\x00&\xb0\x91\x00&\xaf\x95\x00&\xad\x9a\x00\'\xac\x9e\x00(\xaa\xa2\x00)\xa9\xa6\x00)\xa7\xaa\x00*\xa5\xae\x00+\xa3\xb2\x00,\xa1\xb6\x00,\x9e\xb9\x00-\x9c\xbc\x00-\x9a\xbf\x00-\x97\xc2\x00-\x95\xc5\x00,\x92\xc7\x00+\x8f\xc9\x00*\x8c\xcb\x00)\x88\xcd\x00\'\x85\xce\x00&\x81\xcf\x00$}\xd0\x00"y\xd1\x00 u\xd2\x00\x1ep\xd3\x00\x1cl\xd3\x00\x1ag\xd3\x00\x18c\xd3\x00\x16^\xd3\x00\x14Z\xd2\x00\x12U\xd2\x00\x10Q\xd1\x00\x0eL\xd0\x00\rH\xcf\x00\x0bD\xce\x00\n@\xcc\x00\t=\xcb\x00\x089\xc9\x00\x076\xc7\x00\x063\xc5\x00\x050\xc3\x00\x04,\xc0\x00\x03)\xbd\x00\x03&\xbb\x00\x02#\xb7\x00\x02 \xb4\x00\x01\x1d\xb0\x00\x01\x1b\xad\x00\x01\x18\xa9\x00\x01\x15\xa4\x00\x01\x13\xa0\x00\x00\x10\x9b\x00\x01\x0e\x96\x00\x01\x0c\x91\x00\x01\n\x8c\x00\x01\x07\x86\x00\x02\x05\x80\x00\x02\x04z\x00'

USE_PALETTE = PLASMA

SEED_AT = 1000  # Which generation to run to until re-seeding, 0 to never re-seed

# Setup for the display
i75 = Interstate75(
    display=DISPLAY_INTERSTATE75_128X128, stb_invert=False, panel_type=Interstate75.PANEL_GENERIC)
display = i75.display

# These need to be constants for the viper optimized block below.
WIDTH = const(128)
HEIGHT = const(128)


BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(200, 0, 0)


@micropython.viper
def compute_gol(board: ptr8, new_board: ptr8):  # noqa: F821
    for y in range(HEIGHT):
        alive = 0
        if y > 0:
            alive += board[(y - 1) * WIDTH] & 0x80
            alive += board[(y - 1) * WIDTH + 1] & 0x80

        alive += board[y * WIDTH + 1] & 0x80

        if y < HEIGHT - 1:
            alive += board[(y + 1) * WIDTH] & 0x80
            alive += board[(y + 1) * WIDTH + 1] & 0x80

        cur_val = board[y * WIDTH]
        if alive == 0x180:
            new_board[y * WIDTH] = 0x80
        elif alive == 0x100 and cur_val == 0x80:
            new_board[y * WIDTH] = cur_val
        elif cur_val > 0:
            new_board[y * WIDTH] = cur_val - 1
        else:
            new_board[y * WIDTH] = 0

        for x in range(1, WIDTH - 1):
            alive = 0
            if y > 0:
                alive += board[(y - 1) * WIDTH + x - 1] & 0x80
                alive += board[(y - 1) * WIDTH + x] & 0x80
                alive += board[(y - 1) * WIDTH + x + 1] & 0x80

            alive += board[y * WIDTH + x - 1] & 0x80
            alive += board[y * WIDTH + x + 1] & 0x80

            if y < HEIGHT - 1:
                alive += board[(y + 1) * WIDTH + x - 1] & 0x80
                alive += board[(y + 1) * WIDTH + x] & 0x80
                alive += board[(y + 1) * WIDTH + x + 1] & 0x80

            cur_val = board[y * WIDTH + x]
            if alive == 0x180:
                new_board[y * WIDTH + x] = 0x80
            elif alive == 0x100 and cur_val == 0x80:
                new_board[y * WIDTH + x] = cur_val
            elif cur_val > 0:
                new_board[y * WIDTH + x] = cur_val - 1
            else:
                new_board[y * WIDTH + x] = 0

        alive = 0
        if y > 0:
            alive += board[y * WIDTH - 2] & 0x80
            alive += board[y * WIDTH - 1] & 0x80
        alive += board[(y + 1) * WIDTH - 2] & 0x80

        if y < HEIGHT - 1:
            alive += board[(y + 2) * WIDTH - 2] & 0x80
            alive += board[(y + 2) * WIDTH - 1] & 0x80

        cur_val = board[(y + 1) * WIDTH - 1]
        if alive == 0x180:
            new_board[(y + 1) * WIDTH - 1] = 0x80
        elif alive == 0x100 and cur_val == 0x80:
            new_board[(y + 1) * WIDTH - 1] = cur_val
        elif cur_val > 0:
            new_board[(y + 1) * WIDTH - 1] = cur_val - 1
        else:
            new_board[(y + 1) * WIDTH - 1] = 0


@micropython.viper
def viper_display(source: ptr8, dest: ptr32, palette: ptr32):  # noqa: F821
    for offset in range(HEIGHT * WIDTH):
        # The framebuffer is in the format __RRGGBB, eg: 0x000000ff is blue and 0x00ff0000 is red
        # You can play with the values below to change the colour of the life animations.
        # We've created some presets for inspiration!

        # Palette Life
        dest[offset] = palette[source[offset]] if source[offset] < 0x80 else 0x00ffffff

        # Blue Life
        # dest[offset] = source[offset] if source[offset] < 0x80 else 0x009696ff

        # Green Life
        # dest[offset] = source[offset] << 8 if source[offset] < 0x80 else 0x0096ff96

        # Red Life
        # dest[offset] = source[offset] << 16 if source[offset] < 0x80 else 0x00ff9696

        # Purple Life
        # dest[offset] = (source[offset] << 16) | source[offset] if source[offset] < 0x80 else 0x00ff96ff

        # Yellow Life
        # dest[offset] = (source[offset] << 16) | (source[offset] << 8) if source[offset] < 0x80 else 0x00ffff96

        # Teal Life
        # dest[offset] = (source[offset] << 8) | source[offset] if source[offset] < 0x80 else 0x0096ffff


@micropython.viper
def make_display_ptr32(display) -> ptr32:  # noqa: F821
    return ptr32(memoryview(display))      # noqa: F821


class GameOfLife:
    def __init__(self, randomize=True, palette=PLASMA):
        self.palette = palette

        self.board = bytearray(WIDTH * HEIGHT)
        self.back_board = bytearray(WIDTH * HEIGHT)

        if randomize:
            self.seed_life()

    def seed_life(self):
        for i in range(WIDTH * HEIGHT):
            if randint(0, 3) == 3:
                self.board[i] = 0x80

    @micropython.native
    def compute(self):
        compute_gol(self.board, self.back_board)
        self.board, self.back_board = self.back_board, self.board

    def display(self, display):
        dest = make_display_ptr32(display)
        viper_display(self.board, dest, self.palette)

    def load_rle(self, filename):
        with open(filename, "r") as f:
            first_line = True
            pattern_width = 0
            pattern_height = 0
            finished = False

            while not finished:
                line = f.readline()
                if len(line) == 0:
                    break

                line = line.strip()
                if line[0] == "#":
                    continue

                if first_line:
                    params = line.split(",")
                    for param in params:
                        key, value = param.split("=")
                        key = key.strip()
                        value = value.strip()
                        if key == "x":
                            pattern_width = int(value)
                        elif key == "y":
                            pattern_height = int(value)
                        else:
                            print(f"Unknown header param: {key} = {value}")

                    first_line = False
                    y = (HEIGHT - pattern_height) // 2
                    x = (WIDTH - pattern_width) // 2
                    continue

                start = 0
                while start < len(line):
                    if line[start] == "!":
                        finished = True
                        break

                    m = re.match(r"([0-9]*)([bo$])", line[start:])
                    if m is not None:
                        repeat = 1
                        if len(m.group(1)) > 0:
                            repeat = int(m.group(1))

                        if m.group(2) == "$":
                            y += repeat
                            x = (WIDTH - pattern_width) // 2
                        elif m.group(2) == "o":
                            for _ in range(repeat):
                                self.board[y * WIDTH + x] = 0x80
                                x += 1
                        else:
                            x += repeat

                        start += len(m.group(0))
                    else:
                        raise Exception(f"Pattern parse error at {line[start:]}")


# Set randomize to False if you are going to load a file.
gol = GameOfLife(randomize=True, palette=USE_PALETTE)

# R-pentomino
# gol.board[WIDTH*30 + 128] = 0x80
# gol.board[WIDTH*30 + 129] = 0x80
# gol.board[WIDTH*31 + 127] = 0x80
# gol.board[WIDTH*31 + 128] = 0x80
# gol.board[WIDTH*32 + 128] = 0x80

# gol.load_rle("p120gun.rle")

# time.sleep(4)

gen = 0
t_frames = 0
t_total = 0

while True:
    t_start = time.ticks_ms()

    gol.compute()
    t_end = time.ticks_ms()
    gol.display(display)

    gen += 1
    display.set_pen(RED)
    display.text(f"{gen}", 1, 0, scale=1)
    i75.update()
    time.sleep(0.001)

    if SEED_AT and gen == SEED_AT:
        gol.seed_life()
        gen = 0

    t_end = time.ticks_ms()

    t_total += time.ticks_diff(t_end, t_start)
    t_frames += 1

    if t_frames == 100:
        per_frame_avg = t_total / t_frames
        print(f"100 frames in {t_total}ms, avg {per_frame_avg:.02f}ms per frame, {1000 / per_frame_avg:.02f} FPS")
        t_frames = 0
        t_total = 0
