#!/usr/bin/env python3

from collections import namedtuple, Counter
from itertools import chain
import os.path
import sys
from PIL import Image
from PIL.Image import Dither
from PIL.Image import Transpose

# Only map images specified here are supported.
# Note that there is not currently much chance
# that it is possible to support more maps
# by just adding some data here. More likely
# other parts of the script have to be modified
# as well to support whatever differences there
# may be between different maps.

Edge = namedtuple('Edge',
                  ('name', 'colors', 'minwidth', 'maxwidth'))

ROAD_COLORS = ((174, 105, 17), (127, 24, 8))
WATER_COLORS = ((88, 159, 238), (68, 168, 237))

IGNORE_COLORS = ((135, 182, 237))

SUPPORTED_IMAGES = {
    'Yz10cvV.jpeg' : {
        'game' : 'Main Battle Tank: Central Germany',
        'output': 'main_battle_tank_central_germany',
        'size' : (1256, 1622),
        'transpose' : Transpose.ROTATE_270,
        'columnxs' : (103, 139, 177, 212, 248, 283, 319, 356, 391, 426,
                      467, 498, 533, 570, 607, 642, 679, 715, 751, 787,
                      828, 861, 896, 932, 967, 1003, 1037, 1073, 1108, 1143,
                      1184, 1215, 1251, 1287, 1324, 1360, 1395, 1431, 1467, 1502),
        'rowys' : (83, 121, 156, 192, 229, 265, 304, 338, 375, 411,
                   452, 484, 521, 557, 593, 630, 665, 701, 739, 776,
                   818, 848, 885, 921, 958, 994, 1029, 1066, 1101, 1138),
        'squares' : (40, 30),
        'squaresize' : 24, #inner size of square to analyze
        'squarejump' : 1435/40, # how far to jump to next square,
        'terrain_colors' : {
            'woods' : (122, 176, 129),
            'orchard' : (156, 199, 124),
            'urban' : (251, 253, 1)
            },
        'elevation_colors' : (
            (255, 255, 247),
            (230, 207, 114),
            (211, 174, 81),
            (194, 149, 46)
        ),
        'connection_colors' : (
            Edge('2nd class road', ROAD_COLORS, 3, 5),
            Edge('1st class road', ROAD_COLORS, 6, 11),
            Edge('stream', WATER_COLORS, 3, 5),
            Edge('river', WATER_COLORS, 6, 11)
        ),
        'fixes' : {}
    }
}

def print_square_data(image, column, row,
                      x1, y1, x2, y2,
                      terrain_colors,
                      elevation_colors,
                      connection_colors):
    terrain_counter = Counter()
    elevation_counter = Counter()
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            pass
            #image.putpixel((x, y), (255, 0, 0))
    print(column, row, x1, y1, x2, y2)

def print_map_data(image, config):
    colors = tuple(chain(
        chain.from_iterable(config['terrain_colors'].values()),
        chain.from_iterable(config['elevation_colors']),
        chain.from_iterable(ROAD_COLORS),
        chain.from_iterable(WATER_COLORS)))
    colors += (0,) * (768 - len(colors))
    if image.size != config['size']:
        sys.exit('Wrong image size')
    if 'transpose' in config:
        image = image.transpose(config['transpose'])
    paletteimage = Image.new('P', (1, 1), 0)
    print(colors)
    paletteimage.putpalette(colors)
    image = image.quantize(palette=paletteimage, dither=Dither.NONE)
    for row in range(1, config['squares'][1]+1):
        y1 = config['rowys'][row-1]
        y2 = y1 + config['squaresize']
        for column in range(1, config['squares'][0]+1):
            x1 = config['columnxs'][column-1]
            x2 = x1 + config['squaresize']

            print_square_data(image, column, row,
                              x1, y1, x2, y2,
                              config['terrain_colors'],
                              config['elevation_colors'],
                              config['connection_colors']) # TODO add fixes
    image.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} imagefilename')
    filename = sys.argv[1]
    basename = os.path.basename(filename)
    if not basename in SUPPORTED_IMAGES:
        sys.exit(f'Unknown file {basename}')
    with Image.open(filename) as image:
        print_map_data(image, SUPPORTED_IMAGES[basename])
