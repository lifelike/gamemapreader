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
            (122, 176, 129) : 'woods',
            (156, 199, 124) : 'orchard',
            (251, 253, 1) : 'urban'
            },
        'elevation_colors' : (
            (255, 255, 247),
            (230, 207, 114),
            (211, 174, 81),
            (194, 149, 46)
        ),
        'fixes' : {}
    }
}

TERRAIN_THRESHOLD = 100
ELEVATION_THRESHOLD = 25

CSV_HEADER = '"column","row","terrain","elevation","1st class roads","2nc class roads","rivers","streams"'

def print_square_data(image, column, row,
                      x1, y1, x2, y2,
                      terrain_colors,
                      elevation_colors,
                      output):
    terrain_counter = Counter()
    elevation_counter = Counter()
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            color = image.getpixel((x, y))
            if color in terrain_colors:
                terrain_counter[color] += 1
            elif color in elevation_colors:
                elevation_counter[color] += 1
            #image.putpixel((x, y), (255, 0, 0))
    most_terrain = terrain_counter.most_common(1)
    most_elevation = elevation_counter.most_common(1)

    terrain = 'open'
    if len(most_terrain) > 0 and most_terrain[0][1] > TERRAIN_THRESHOLD:
        terrain = terrain_colors[most_terrain[0][0]]
    elevation = -1
    if len(most_elevation) > 0 and most_elevation[0][1] > ELEVATION_THRESHOLD:
        elevation = elevation_colors.index(most_elevation[0][0])

    # XXX quick fix to set elevation of urban squares
    # XXX that happens to work for this particular game
    if terrain == 'urban':
        if column <= 5 or (column, row) == (16, 13):
            elevation = 2
        elif column <= 28:
            elevation = 1
        else:
            elevation = 0
    print(f'{column},{row},"{terrain}",{elevation},"","","",""', file=output)

def print_map_data(image, config):
    colors = tuple(chain(
        chain.from_iterable(config['terrain_colors'].keys()),
        chain.from_iterable(config['elevation_colors'])))
    colors += (0,) * (768 - len(colors))
    if image.size != config['size']:
        sys.exit('Wrong image size')
    if 'transpose' in config:
        image = image.transpose(config['transpose'])
    paletteimage = Image.new('P', (1, 1), 0)
    paletteimage.putpalette(colors)
    image = image.quantize(palette=paletteimage, dither=Dither.NONE).convert(mode='RGB')
    with open(config['output'] + '.csv', 'w') as output:
        print(CSV_HEADER, file=output)
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
                                  output)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'usage: {sys.argv[0]} imagefilename')
    filename = sys.argv[1]
    basename = os.path.basename(filename)
    if not basename in SUPPORTED_IMAGES:
        sys.exit(f'Unknown file {basename}')
    with Image.open(filename) as image:
        print_map_data(image, SUPPORTED_IMAGES[basename])
