#!/usr/bin/env python
"""
Generate a numbered quilt image for checking viewpoints and crosstalk

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

import sys, random, colorsys
from PIL import Image, ImageDraw, ImageFont

def usage():
    print('usage: %s <tilesh> <tilesv> <quilt-image> [<quiltw> <quilth>]' % sys.argv[0])
    print()
    sys.exit(-1)
    
if len(sys.argv) not in [4,6]:
    usage()
    
tiles_h = int(sys.argv[1])
tiles_v = int(sys.argv[2])
quilt_image_file = sys.argv[3]

quilt_w = 2048
quilt_h = 2048

if len(sys.argv) == 6:
    quilt_w = int(sys.argv[4])
    quilt_h = int(sys.argv[5])
    
tile_w = quilt_w // tiles_h
tile_h = quilt_h // tiles_v

AREA_SPLIT = 3

area_w = tile_w // AREA_SPLIT
area_h = tile_h // AREA_SPLIT

print('tile:', tile_w, tile_h)
  
outimg = Image.new('RGB', (quilt_w, quilt_h))

tile_idx = 1
tile_top = quilt_h - tile_h

font = ImageFont.truetype('/usr/share/fonts/TTF/FreeSansBold.ttf', size=tile_h//9)

for j in range(tiles_v):
    
    tile_left = 0
    for i in range(tiles_h):
        
        hue = (tile_idx % 12) / 12
        col = tuple(map(lambda v: int(255*v), colorsys.hsv_to_rgb(hue, 0.8, 0.7)))
        
        tile_img = Image.new('RGB', (tile_w, tile_h), col)
        
        draw = ImageDraw.Draw(tile_img)
        
        txt = str(tile_idx)
        txtsz = draw.textsize(txt, font=font)
        
        # Split the tile image into 3x3 areas, within each area we show the tile number
        # once. The exact placement of each number within the area depends on the tile 
        # number itself, as we expect number close in value to be shown concurrently
        
        oidx = tile_idx % 9
        
        for aj in range(AREA_SPLIT):
            area_top = aj * area_h
            
            for ai in range(AREA_SPLIT):
                area_left = ai * area_w
                
                # Centered in area
                x = area_left + area_w/2 - txtsz[0]/2
                y = area_top + area_h/2 - txtsz[1]/2
                
                # Offset based on tile index
                x += ((oidx % AREA_SPLIT) - 1) * area_w/AREA_SPLIT
                y += ((oidx // AREA_SPLIT) - 1) * area_h/AREA_SPLIT
                
                # White outline
                for xo in [-2,2]:
                    for yo in [-2,2]:
                        draw.text((x+xo, y+yo), txt, font=font, fill='white')
                
                draw.text((x, y), txt, font=font, fill='black')
                
        del draw
        
        outimg.paste(tile_img, (tile_left, tile_top))
    
        tile_idx += 1
        tile_left += tile_w
        
    tile_top -= tile_h
    
        
outimg.save(quilt_image_file)
