#!/usr/bin/env python
# 
# Take a non-standard linear Looking Glass quilt image and convert it into
# a "native" image that can be displayed directly on a specific LG.
# 
# A linear quilt has all view images side-by-side in sequence:
#  
#     0   1   2   3 ... 44
#  
# The tile index is therefore equal to the view number.
#  
# Partly based on https://github.com/lonetech/LookingGlass/blob/master/quiltshader.glsl
# (for which no license seems to be specified)
# 
#
# Copyright (c) 2019, SURFsara BV
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of SURFsara BV nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL SURFSARA BV BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys, json
from math import atan, cos, floor
from PIL import Image

from calibration import Calibration

def usage():
    print('usage: %s <visual.json> <quilt-image> [tilesh] <native-image>' % sys.argv[0])
    print()
    sys.exit(-1)
    
if len(sys.argv) not in [3,5]:
    usage()


calibration = Calibration(sys.argv[1])
screenW = calibration.screenW
screenH = calibration.screenH
tilt = calibration.tilt
pitch = calibration.pitch
center = calibration.center
subp = calibration.subp

quilt_image_file = sys.argv[2]
if len(sys.argv) == 5:
    TILES = int(sys.argv[3])
    native_image_file = sys.argv[4]
else:
    TILES = 45
    native_image_file = sys.argv[3]
    
INV_TILES = 1.0 / TILES
        

def quilt_map(pos, a):

    # Y major positive direction, X minor negative direction
    tile = [TILES - 1, 0]
    
    a = a%1 
    tile[1] += floor(a)
    a = a%1 * TILES
    tile[0] += -floor(a)
    
    res = [pos[0] + tile[0], pos[1] + tile[1]]
    
    res[0] *= INV_TILES
    
    return res


def quilt_tile(a):

    tile = TILES - 1    
    a = a%1 * TILES
    tile -= floor(a)
    
    return tile


def pixel_color(qpx, u, v):
    
    a = (u + (1.0 - v)*tilt)*pitch - center
    
    tile = quilt_tile(a)
    r_pos = (
        (u + tile) * INV_TILES,
        v 
    )
    
    tile = quilt_tile(a + subp)
    g_pos = (
        (u + tile) * INV_TILES,
        v
    )    
    
    tile = quilt_tile(a + 2*subp)
    b_pos = (
        (u + tile) * INV_TILES,
        v
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
