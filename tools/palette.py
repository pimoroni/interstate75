from matplotlib import pyplot
import numpy

# This script generates a 128 entry palette as a 512byte bytearray.
# When used in Viper it can be cast to uint32 giving fast lookup to RGB888 compatible colours
# Find palette images here: https://matplotlib.org/stable/users/explain/colors/colormaps.html

PALETTE = "nipy_spectral"
NUM_ENTRIES = 128
MIN_BRIGHTNESS = float(128)
MAX_BRIGHTNESS = float(255)

# Forces a hard rolloff to black at the lower end
# So the display doesn't stay lit up
FADEOUT_LENGTH = 5

# Get 128 colours
colourmap = pyplot.get_cmap(PALETTE, NUM_ENTRIES)
colours = colourmap(range(0, NUM_ENTRIES)).astype('float')

if FADEOUT_LENGTH > 0:
    fadeout_length = FADEOUT_LENGTH + 1

    colours[1:FADEOUT_LENGTH + 1, :] *= numpy.dstack(
        [
            numpy.linspace(0, 1, FADEOUT_LENGTH),
            numpy.linspace(0, 1, FADEOUT_LENGTH),
            numpy.linspace(0, 1, FADEOUT_LENGTH),
            numpy.zeros(FADEOUT_LENGTH), # Unused byte
        ]
    )[0]

    # Always zero out the first colour,
    # the way GOL works causes some oscillation between the two minimum states
    # resulting in visual flicker if we don't do this!
    # (we're kinda hoping the first fadeout value is also 0)
    colours[0, :] *= 0


# Scale them to 0-255
scale = numpy.dstack(
    [
        numpy.logspace(numpy.log10(MIN_BRIGHTNESS), numpy.log10(MAX_BRIGHTNESS), NUM_ENTRIES),
        numpy.logspace(numpy.log10(MIN_BRIGHTNESS), numpy.log10(MAX_BRIGHTNESS), NUM_ENTRIES),
        numpy.logspace(numpy.log10(MIN_BRIGHTNESS), numpy.log10(MAX_BRIGHTNESS), NUM_ENTRIES),
        numpy.zeros(NUM_ENTRIES),
    ]
)[0]

colours *= scale

# Convert to uint8
colours = numpy.clip(colours, 0, 255).astype('uint8')

# Reshape to four byte uint32s
colours = colours.reshape(NUM_ENTRIES, 4)

# Flip our colour bytes into the right order
colours = numpy.array(numpy.flip(colours, 1))

# Roll the unused byte onto the end
colours = numpy.array(numpy.roll(colours, -1, 1))

# View as uint32 -> 4 bytes become one uint32
uint32_colours = colours.view('uint32')

# Reshape to a single array of colours
uint32_colours = uint32_colours.reshape(NUM_ENTRIES)

# Mask out the unused byte
#uint32_colours &= 0x00ffffff

colourmap = ",".join([f"0x{c:04x}" for c in uint32_colours])

print(colourmap)

print("")
print(uint32_colours.tobytes())
print("")