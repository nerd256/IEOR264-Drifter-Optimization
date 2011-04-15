# -*- coding: utf-8 -*-
 
# -*- coding: utf-8 -*-
import os,sys
import Image
from random import random
import ImageFilter, ImageDraw

boatimg = Image.open("boat.png");
boatimg_rev = boatimg.transpose(Image.FLIP_TOP_BOTTOM);

img = Image.open("labelled_rivers.png");
pix = img.load();

(W, H) = img.size;
outimg = Image.new('RGB',(W+50,H),(255,255,255));
outpix = outimg.load();
outdraw = ImageDraw.Draw(outimg)


colors = [];
for i in range(0,1000):
    colors.append((random()*128+128,random()*128+128,random()*128+128));
colors[0] = (255,0,0);
colors[1] = (0,255,0);
colors[2] = (0,0,255);
colors[3] = (255,255,0);
colors[4] = (0,255,255);
colors[5] = (255,0,255);

fin = open("boat_paths.txt","r")
TIME = int(fin.readline());
BOATTIME = int(fin.readline());
paths = [];
boat_carrying = [0]*(TIME/BOATTIME/2);
for line in fin:
    (boatidx, pathstr) = line.split(';');
    btime = int(boatidx) * BOATTIME * 2;
    path = [int(k) for k in pathstr.split(',')];
    paths.append((btime,path));
    boat_carrying[int(boatidx)] += 1;
    
fin.close();
print boat_carrying

for t in range(TIME):
    bidx = int( t / (TIME/BOATTIME) ) + 1;
    labs = [];
    for (btime, path) in paths:
        if ( btime <= t and t-btime < len(path) ) :
            labs.append(path[t-btime]);
            #print path[t-btime];
    
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

    # draw boat location
    outdraw.rectangle((W,0)+(W+50,H),fill=(255,255,255));
    outdraw.line((W,0)+(W,H), fill=(0,0,0));
    for yi in range(0,BOATTIME+1):
        y = yi * H/BOATTIME;
        
        outdraw.line((W,y)+(W+50,y),fill=(0,0,0));

    
    boatpos = t % (BOATTIME*2);
    boatdir = int( boatpos / BOATTIME );
    if ( boatdir == 1 ):
        if ( bidx < len(boat_carrying) ):
            boatpos = 2*BOATTIME - 1 - boatpos
            outimg.paste(boatimg,(W+10,boatpos*H/BOATTIME + 15));
            outdraw.text((W+2,boatpos * H/BOATTIME+50),"CARRYING",fill=(0,0,0));
            outdraw.text((W+2,boatpos * H/BOATTIME+60),"%d UNITS"%(boat_carrying[bidx]),fill=(0,0,0));
        else:
            boatpos = BOATTIME-1;
            outimg.paste(boatimg_rev,(W + 10, boatpos*H/BOATTIME + 15));
            outdraw.text((W+2,boatpos * H/BOATTIME+50),"RETURN",fill=(0,0,0));
            outdraw.text((W+2,boatpos * H/BOATTIME+60)," HOME",fill=(0,0,0));
    else:
        outimg.paste(boatimg_rev,(W + 10, boatpos*H/BOATTIME + 15));
    
    
    print t
    outimg.save("vizout/boat%04d.png"%t);
