#!/usr/bin/env python
"""
Take a set of separate view images (i.e. the tiles that normally
make up a quilt) and convert them to a "native" image that can be 
displayed directly on a specific LG.

Partly based on https://github.com/lonetech/LookingGlass/blob/master/quiltshader.glsl
"""

import sys, json
from math import atan, cos, floor
from PIL import Image

from calibration import Calibration

def usage():
    print('usage: %s <visual.json> <frame-pattern> <first> <last> <native-image>' % sys.argv[0])
    print()
    sys.exit(-1)
    
if len(sys.argv) != 6:
    usage()


calibration = Calibration(sys.argv[1])
screenW = calibration.screenW
screenH = calibration.screenH
tilt = calibration.tilt
pitch = calibration.pitch
center = calibration.center
subp = calibration.subp

frame_file_pattern = sys.argv[2]
frame_file_first = int(sys.argv[3])
frame_file_last = int(sys.argv[4])

native_image_file = sys.argv[5]

NUM_FRAMES = frame_file_last - frame_file_first + 1
INV_NUM_FRAMES = 1.0 / NUM_FRAMES

# Load tiles

tile_images = []    # For holding references to image objects
tile_pixels = []    # For PixelAccess objects

FRAME_WIDTH = FRAME_HEIGHT = None

for i in range(NUM_FRAMES):
    tile_file = frame_file_pattern % (frame_file_first + i)
    #print(tile_file)
    img = Image.open(tile_file)
    tile_images.append(img)
    tile_pixels.append(img.load())
    if FRAME_WIDTH is None:
        FRAME_WIDTH, FRAME_HEIGHT = img.size
        
print('Tile size %d x %d' % (FRAME_WIDTH, FRAME_HEIGHT))

def determine_view(a):
    res = NUM_FRAMES - 1
    a = a%1 * NUM_FRAMES
    res -= floor(a)
    return res
    
def pixel_color(u, v):
    
    j = int(v * FRAME_HEIGHT)
    
    a = (u + (1.0 - v)*tilt)*pitch - center

    # Red
    view = determine_view(a)
    pos = (u + view) * INV_NUM_FRAMES
    i = int(pos * FRAME_WIDTH * NUM_FRAMES)
    local_i = i % FRAME_WIDTH
    img = tile_pixels[view]
    r = img[local_i,j][0]
    
    # Green
    view = determine_view(a+subp)
    pos = (u + view) * INV_NUM_FRAMES
    i = int(pos * FRAME_WIDTH * NUM_FRAMES)
    local_i = i % FRAME_WIDTH
    img = tile_pixels[view]
    g = img[local_i,j][1]
    
    # Blue
    view = determine_view(a+2*subp)
    pos = (u + view) * INV_NUM_FRAMES
    i = int(pos * FRAME_WIDTH * NUM_FRAMES)
    local_i = i % FRAME_WIDTH
    img = tile_pixels[view]
    b = img[local_i,j][2]
        
    return (r, g, b)
    
outimg = Image.new('RGB', (screenW, screenH))
opx = outimg.load()

for j in range(screenH):
    v = (j+0.5) / screenH
    
    for i in range(screenW):
        u = (i+0.5) / screenW
        
        opx[i,j] = pixel_color(u, v)
        
del opx
outimg.save(native_image_file)
