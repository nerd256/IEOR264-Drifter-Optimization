# -*- coding: utf-8 -*-
import os,sys
import Image
import ImageFilter, ImageDraw

img = Image.open("rivers.png");
pix = img.load();

pathimg = Image.new('L',img.size,255);
pathpx = pathimg.load()
pathdraw = ImageDraw.Draw(pathimg)

greens = [];
reds = [];

for y in range(0,img.size[1]):
    for x in range(0,img.size[0]):
        if ( pix[x,y][2] < 255 ):
            if ( pix[x,y][0] == 255 ) :
                reds.append((x,y));
                pix[x,y] = (0,0,0);
            elif ( pix[x,y][1] == 255 ) :
                #print x,y
                greens.append((x,y));
                pix[x,y] = (0,0,0);

            #print x,y,pix[x,y]      

gx,gy = greens[0];
i = 0;

for xd in [-1,0,1]:
    for yd in [-1,0,1]:
        pix[gx+xd,gy+yd] = (0,255,0);

pix[gx,gy] = (0,128,0);

img.save("frames/%04d.png" % i);
i += 1;

done = False;
while not done:
    lastimg = img;
    lastpix = pix;
    
    img = img.copy();
    pix = img.load();
        
    done = True
    for y in range(0,img.size[1]):
        for x in range(0,img.size[0]):
            if ( lastpix[x,y][1] == 255 and lastpix[x,y][0] == 0):
                pix[x,y] = (0,128,0);
                for xd in [-1,0,1]:
                    for yd in [-1,0,1]:
                        if ( x+xd > 0 and x+xd < img.size[0] and y+yd > 0 and y + yd < img.size[1] and lastpix[x+xd,y+yd][1] == 0 ):
                            pix[x+xd,y+yd] = (0,255,0);
                            done = False
    print i
    img.save("frames/%04d.png" % i);
                       
    """for y in range(0,img.size[1]):
        for x in range(0,img.size[0]):
            if pix[x,y][1] == 255 and pix[x,y][0] == 0 :
                pix[x,y] = (0,128,0);
    """            
    
    i += 1;

"""
inwater = False;
chans = []
watstartx = 0;

for y in range(0,img.size[1]):
    numchans = 0;
    for x in range(0,img.size[0]):
        if not inwater and pix[x,y][0] == 0:
            inwater = True;
            watstartx = x;
        elif inwater and pix[x,y][0] == 255:
            inwater = False;
            numchans += 1
    if inwater:
        pathimg[int((x+img.size[0])/2),y] = 0;
        numchans += 1
    chans.append(numchans);

for y in range(1,len(chans)-1):
    if ( chans[y] > chans[y-1] and chans[y+1] >= chans[y] ):
        for x in range(0,img.size[0]):
            pix[x,y] = (0,255,0);
    elif ( chans[y] < chans[y-1] and chans[y+1] <= chans[y]):
        for x in range(0,img.size[0]):
            pix[x,y] = (255,0,0);
"""     

img.show();

print "reds",reds
print "greens",greens
# Use blue band for river
