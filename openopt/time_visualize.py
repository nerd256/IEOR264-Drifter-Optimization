# -*- coding: utf-8 -*-
import os,sys
import Image
from random import random
import ImageFilter, ImageDraw

img = Image.open("labelled.png");
pix = img.load();

outimg = Image.new('RGB',img.size,(255,255,255));
outpix = outimg.load();

colors = [];
for i in range(0,1000):
    colors.append((random()*128+128,random()*128+128,random()*128+128));
colors[0] = (255,0,0);
colors[1] = (0,255,0);
colors[2] = (0,0,255);
colors[3] = (255,255,0);
colors[4] = (0,255,255);
colors[5] = (255,0,255);

paths = []
fin = open("taken_paths.txt","r");
timeH = 0;
for line in fin:
    try:
        line = line[line.index(':')+1:];
    except:pass
    
    path = [int(i) for i in line[:-1].split(',')];
    paths.append(path);
    if ( len(path) > timeH ):
        timeH = len(path);
    
fin.close();
print "Loaded",len(paths),"paths maxlen=",timeH
for t in range(0,timeH):
    print "t =",t
    labs = [];
    for path in paths:
        if ( t < len(path) ) :
            labs.append(path[t]);
    
    # now make an image
    for y in range(0,img.size[1]):
        for x in range(0,img.size[0]):
            if ( pix[x,y][0] == 255 ):
                outpix[x,y] = (255,255,255);
            elif (pix[x,y][0] in labs):
                outpix[x,y] = colors[pix[x,y][0]];
            else:
                #print pix[x,y]
                outpix[x,y] = (0,0,0);

    outimg.save("vizout/time%04d.png"%t);
    
for t in range(0,10):
    outimg.save("vizout/time%04d.png"%(timeH+t));