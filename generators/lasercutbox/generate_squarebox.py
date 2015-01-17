# -*- coding: utf-8 -*-
"""
Generating square box for lasercutter

@author: Benny Malengier

Based on: http://hamsterworks.co.nz/mediawiki/index.php/Svg_box
"""


from __future__ import print_function, division
import sys

import subprocess

#first argument must be the image file
import argparse
parser = argparse.ArgumentParser(description='Output svg of a box for lasercutting')
parser.add_argument('filename', help='filename of output svg image')
parser.add_argument('-i', '--info', action='store_true',
                    help="show information")
parser.add_argument('-o', '--openlid', action='store_true',
                    help="Create an box with no lid, so open at top")
parser.add_argument('-W', '--width', help="Width of the box in mm. Default 100mm")
parser.add_argument('-H', '--heigth', help="Height of the box in mm. Default 100mm")
parser.add_argument('-D', '--depth', help="Depth of the box in mm. Default 50mm")

parser.add_argument('-m', '--mitersize', help="Size of miter in mm. Default 10mm")

parser.add_argument('-t', '--thickness', help="Thickness of material in mm. Default 3.0")
parser.add_argument('-k', '--kerf', help="Kerf of laserbeam (width of the cut) in mm."
                                         " See http://blog.ponoko.com/2008/09/11/how-much-material-does-the-laser-burn-away/. "
                                         "Default 0.16mm")

inputdata = parser.parse_args() #parse arg from sys.argv


outfilename = inputdata.filename
info = inputdata.info
openlid = inputdata.openlid
if not openlid:
    openlid = 0

def set_default(value, default):
    if value is None:
        return default
    else:
        return float(value)

#***
# start of svg file. Param: width and height of the svg in mm
#**

svgfile = ""

def StartDoc(widthsvg, heigthsvg):
    wcm = widthsvg *1.01 / 10
    hcm = heigthsvg *1.01 / 10
    svgfile = "<?xml version=\"1.0\" standalone=\"no\"?>\r\n"
    svgfile += "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\r\n"
    svgfile += "<svg width=\"%icm\" height=\"%icm\" viewBox=\"0 0 %i %i\" xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\">\r\n" \
                %  (int(wcm), int(hcm), int(widthsvg*10), int(heigthsvg*10) )
    return svgfile

def EndDoc():
    return "</svg>\r\n"

width     = set_default(inputdata.width, 100)
heigth    = set_default(inputdata.heigth, 100)
depth     = set_default(inputdata.depth, 50)
mitersize = set_default(inputdata.mitersize, 10)
kerf      = set_default(inputdata.kerf, 0.16)
thick     = set_default(inputdata.thickness, 3.0)

nrmiterw = int(round(width / mitersize ))
if (nrmiterw % 2 == 0): nrmiterw += 1
if (width/nrmiterw < 2*thick):
    nrmiterw -= 2
nrmiterh = int(round(heigth / mitersize ))
if (nrmiterh % 2 == 0): nrmiterh += 1
if (heigth/nrmiterh < 2*thick):
    nrmiterh -= 2
nrmiterd = int(round(depth / mitersize ))
if (nrmiterd % 2 == 0): nrmiterd += 1
if (depth/nrmiterd < 2*thick):
    nrmiterd -= 2
if nrmiterw < 1 or nrmiterh < 1 or nrmiterd < 1:
    print ("ERROR: reduce mitersize, corners will break off otherwise!")
    sys.exit(0)


def PolyStart():
   return "<polyline points=\""

def PolyPoint(x, y, first=False):
    outp = ""
    if (not first):
        outp = " "
    outp += "%f,%f" % (x,y)
    return outp

def PolyEnd():
    return "\" fill=\"none\" stroke=\"black\" stroke-width=\"3\" />\r\n"

def PathStart(x,y):
    outp = """<path
       style="fill:none;stroke:#000000;stroke-width:1.06200004;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dashoffset:0"
       d="m %f,%f """ % (x,y)
    return outp

def PathEnd():
    return """z"
       id="rect2985"
       inkscape:connector-curvature="0"
       sodipodi:nodetypes="ccccc" />
"""

def PathMove(dx, dy):
    return " %f,%f " % (dx, dy)

#one of 4 size
def side(x,y,w,h,corner_sizex,corner_sizey,thick,cut_width, div_x, div_y,
         invertX, invertY, xm=1,ym=0, openlid=False):
    outp = ""    
    if openlid:
        miter = 0
    else:
        miter = 1
    dx = corner_sizex*xm
    dy = corner_sizey*ym
    if invertX: dx-=thick*xm
    if invertY: dy-=thick*ym
    half_cut = cut_width/2 * (xm+ym)
    if invertY and xm: 
        half_cut = -half_cut
    if invertX and ym: 
        half_cut = -half_cut
    d = xm-ym
    if invertY and xm: d = -d
    if invertX and ym: d = -d
    outp += PathMove(dx+half_cut*abs(xm),dy+half_cut*abs(ym))
    dy = thick *d *abs(xm) *miter
    dx = thick *d *abs(ym) *miter
    d = -d;
    outp += PathMove(dx,dy)
    half_cut = -half_cut

    # All but the center one
    ax = (w-2*corner_sizex) / (2*div_x+1)
    ay = (h-2*corner_sizey) / (2*div_y+1)
    # the center one
    bx = w-2*corner_sizex-ax*(2*div_x)
    by = h-2*corner_sizey-ay*(2*div_y)

    for i in range(0,abs(div_x*xm+div_y*ym)):
        dx = ax*xm
        dy = ay*ym
        outp += PathMove(dx+half_cut*abs(xm),dy+half_cut*abs(ym))
        dy = thick *d*abs(xm) *miter
        dx = thick *d*abs(ym) *miter
        d = -d
        outp += PolyPoint(dx,dy)
        half_cut = -half_cut

    dx = bx*xm;
    dy = by*ym;
    outp += PathMove(dx+half_cut*abs(xm), dy+half_cut*abs(ym))
    dy = thick *d*abs(xm) *miter
    dx = thick *d*abs(ym) *miter
    d = -d
    outp += PathMove(dx, dy)
    half_cut = -half_cut

    for i in range(0,abs(div_x*xm+div_y*ym)):
        dx = ax*xm
        dy = ay*ym
        outp += PolyPoint(dx+half_cut*abs(xm), dy+half_cut*abs(ym))
        dy = thick *d*abs(xm) *miter
        dx = thick *d*abs(ym) *miter
        d = -d
        outp += PathMove(dx, dy)
        half_cut = -half_cut

    dx = corner_sizex*xm
    dy = corner_sizey*ym
    if invertX and xm: dx -= thick * xm
    if invertY and ym: dy -= thick * ym
    outp += PathMove(dx, dy)
    return outp, x, y


#********
# x,y: origin of start in mm
# w,h: width and height in mm
# nrmiterw/h: number of miter intervals along w and h
# thick: thickness of material
# invert: invert in x or y direction the logic
#********
def squareframe(x, y, w, h, nrmiterw, nrmiterh, thick, invertX, invertY, openlid=0):
    outp = ""
    div_x = int((nrmiterw-3) / 2)
    div_y = int((nrmiterh-3) / 2)
    corner_sizex = w/nrmiterw
    corner_sizey = h/nrmiterh
    #convert to 1/10th mm 
    x = 10*x; y=10*y; w=10*w; h=10*h;thick=10*thick
    corner_sizex = corner_sizex*10;corner_sizey = corner_sizey*10
    cut_width = kerf*10
    x = x-w/2
    if invertX: x+=thick
    y = y-h/2
    if invertY: y+=thick
    outp += PathStart(x,y)
    #top side
    dat, x, y = side(x,y,w,h,corner_sizex,corner_sizey,thick,cut_width,
                     div_x,div_y, invertX, invertY, 1, 0, openlid==1)
    outp += dat
    #Right Side
    dat, x, y = side(x,y,w,h,corner_sizex,corner_sizey,thick,cut_width,
                     div_x,div_y, invertX, invertY, 0, 1, openlid==2)
    outp += dat
    # bottom Side
    dat, x, y = side(x,y,w,h,corner_sizex,corner_sizey,thick,cut_width,
                     div_x,div_y, invertX, invertY, -1, 0, openlid==3)
    outp += dat
    # Left side
    dat, x, y = side(x,y,w,h,corner_sizex,corner_sizey,thick,cut_width,
                     div_x,div_y, invertX, invertY, 0, -1, openlid==4)
    outp += dat
    outp += PathEnd()
    return outp


svgfile = StartDoc(2*(5 + width + 5+ depth), 5+heigth+5+depth)
svgfile += squareframe(5+width/2, 5+heigth/2, width, heigth, nrmiterw, nrmiterh,
                       thick, False, False)
if openlid: openlid = 2 #right side
svgfile += squareframe(5+width+5+depth/2, 5+heigth/2, depth, heigth, nrmiterd, nrmiterh,
                       thick, True, False, openlid)
if openlid: openlid = 3 #bottom side
svgfile += squareframe(5+width/2, 5+heigth+5+depth/2, width, depth, nrmiterw, nrmiterd,
                       thick, True, True, openlid)
#repeat again
if not openlid:
    svgfile += squareframe(5+width+5+depth+5+width/2, 5+heigth/2, width, heigth, nrmiterw, nrmiterh,
                           thick, False, False)
if openlid: openlid = 4
svgfile += squareframe(5+width+5+depth+5+width+5+depth/2, 5+heigth/2, depth, heigth, nrmiterd, nrmiterh,
                       thick, True, False, openlid)
if openlid: openlid = 1
svgfile += squareframe(5+width+5+width/2, 5+heigth+5+depth/2, width, depth, nrmiterw, nrmiterd,
                       thick, True, True, openlid)
svgfile += EndDoc()
#write out scad file
if not outfilename[-4:] == ".svg":
    outfilename += ".svg"
    
with open(outfilename, 'w') as fsvg:
    fsvg.write(svgfile)

print ("Generation finished. SVG in", outfilename )
