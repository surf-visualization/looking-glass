#!/usr/bin/env python
"""
Take a "standard" Looking Glass quilt image and convert it into
a "native" image that can be displayed directly on a specific LG.

Partly based on https://github.com/lonetech/LookingGlass/blob/master/quiltshader.glsl

https://forum.lookingglassfactory.com/t/combining-32-views/501/2
The views go from the bottom left as the leftmost view, to the top right being the furthest right
E.g. for a 4x8 quilt:

28  29  30  31
24  25  26  27
20  21  22  23
16  17  18  19
12  13  14  15
 8   9  10  11
 4   5   6   7
 0   1   2   3
"""

import sys, json
from math import atan, cos, floor
from PIL import Image

from calibration import Calibration

def usage():
    print('usage: %s <visual.json> <quilt-image> [tilesh tilesv] <native-image>' % sys.argv[0])
    print()
    sys.exit(-1)
    
if len(sys.argv) not in [4,6]:
    usage()


calibration = Calibration(sys.argv[1])
screenW = calibration.screenW
screenH = calibration.screenH
tilt = calibration.tilt
pitch = calibration.pitch
center = calibration.center
subp = calibration.subp

quilt_image_file = sys.argv[2]
if len(sys.argv) == 6:
    TILES = tuple(map(int, sys.argv[3:5]))
    native_image_file = sys.argv[5]
else:
    TILES = (5, 9)
    native_image_file = sys.argv[3]
    
INV_TILES = (1.0/TILES[0], 1.0/TILES[1])
        

def quilt_map(pos, a):

    # Y major positive direction, X minor negative direction
    tile = [TILES[0] - 1, 0]
    
    a = a%1 * TILES[1]      
    tile[1] += floor(a)
    a = a%1 * TILES[0]
    tile[0] += -floor(a)
    
    res = [pos[0] + tile[0], pos[1] + tile[1]]
    
    res[0] /= TILES[0]
    res[1] /= TILES[1]
    
    return res


def quilt_tile(a):

    # Y major positive direction, X minor negative direction
    tile = [TILES[0] - 1, 0]
    
    a = a%1 * TILES[1]      
    tile[1] += floor(a)     
    a = a%1 * TILES[0]
    tile[0] += -floor(a)
    
    return tile


def pixel_color(qpx, u, v):
    
    a = (u + (1.0 - v)*tilt)*pitch - center
    
    tile = quilt_tile(a)
    r_pos = (
        (u + tile[0]) * INV_TILES[0],
        (v + tile[1]) * INV_TILES[1]
    )
    
    tile = quilt_tile(a + subp)
    g_pos = (
        (u + tile[0]) * INV_TILES[0],
        (v + tile[1]) * INV_TILES[1]
    )    
    
    tile = quilt_tile(a + 2*subp)
    b_pos = (
        (u + tile[0]) * INV_TILES[0],
        (v + tile[1]) * INV_TILES[1]
    )
    
    #print(u, v, a, r_pos, g_pos, b_pos)
    
    # XXX nearest-neighbour sampling
    r = qpx[r_pos[0]*QWIDTH, r_pos[1]*QHEIGHT][0]
    g = qpx[g_pos[0]*QWIDTH, g_pos[1]*QHEIGHT][1]
    b = qpx[b_pos[0]*QWIDTH, b_pos[1]*QHEIGHT][2]

    return (r, g, b)
  

quiltimg = Image.open(quilt_image_file)

QWIDTH, QHEIGHT = quiltimg.size

qpx = quiltimg.load()

outimg = Image.new('RGB', (screenW, screenH))
opx = outimg.load()

# XXX offset with 0.5 a pixel?
for j in range(screenH):
    v = j / screenH
    
    for i in range(screenW):
        u = i / screenW
        
        opx[i,j] = pixel_color(qpx, u, v)
        
del qpx
del opx
outimg.save(native_image_file)
