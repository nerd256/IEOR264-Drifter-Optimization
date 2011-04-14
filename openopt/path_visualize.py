# -*- coding: utf-8 -*-
import os,sys
import Image
from random import random
import ImageFilter, ImageDraw

img = Image.open("labelled_rivers.png");
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

fin = open("paths.txt","r");
pidx = 0;
for line in fin:
    try:
        line = line[line.index(':')+1:];
    except:pass
    
    path = [int(i) for i in line[:-1].split(',')];
    print path
    for y in range(0,img.size[1]):
        for x in range(0,img.size[0]):
            if ( pix[x,y][0] == 255 ):
                outpix[x,y] = (255,255,255);
            elif (pix[x,y][0] in path):
               # print "yoyo"
                outpix[x,y] = colors[pix[x,y][0]];
            else:
                #print pix[x,y]
                outpix[x,y] = (0,0,0);
             
    outimg.save("vizout/path%04d.png"%pidx);
    pidx += 1;
