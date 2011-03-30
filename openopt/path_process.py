# -*- coding: utf-8 -*-
import os,sys
import Image
from random import random
import ImageFilter, ImageDraw

img = Image.open("rivers.png");
pix = img.load();

pathimg = Image.new('RGB',img.size,(255,255,255));
pathpx = pathimg.load()
pathdraw = ImageDraw.Draw(pathimg)

colors = [(128,0,0),(0,128,0),(0,0,128),(128,128,0),(0,128,128),(128,0,128)];


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
pix[gx,gy] = (0,255,0);
used_labels = [0];
edge = [(gx,gy,0)];
newedge = [];
connections = [];
while edge:
    for (x, y, l) in edge:
        for (s, t) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1),(x-1,y-1)):
            if s >= 0 and t >= 0 and s < img.size[0] and t < img.size[1] and \
                pix[s,t][1] != 255 and pix[s,t][0] == 0:
                pix[s,t] = (0,255,0);
                newedge.append((s, t, l))
                
    edge = []

    #print "Iteration %d:"%i
    p = 0;
    labels_seen = [];
    while newedge:
        (x,y,l) = newedge.pop();

        if ( l in labels_seen ): # already saw this label, but not a part of it, a new edge is born!
            old = l;
            while l in used_labels:
                l += 1;
            used_labels.append(l);
            connections.append((old,l)); # split
                    
        labels_seen.append(l);
        
        edge.append((x,y,l));
        tocheck = [(x,y,l)];
        thisedge = [(x,y,l)];
        while tocheck:
            (cx,cy,l) = tocheck.pop();
            for (mx, my) in ((cx+1, cy), (cx-1, cy), (cx,cy+1), (cx, cy-1)):
                for (ox,oy,ol) in newedge:
                    if ( ox == mx and oy == my):
                        newedge.remove((ox,oy,ol));
                        thisedge.append((ox,oy,l));
                        tocheck.append((ox,oy,l));
                        edge.append((ox,oy,l));
                        if ( ol != l and (ol,l) not in connections) :
                            connections.append((ol,l)); #join
                               
        for (x,y,l) in thisedge:
            pathpx[x,y] = (5*l,5*l,5*l);
        
        p += 1;
    
   # pathimg.save("frames/%04d.png"%i);
    i += 1;
    

pathimg.show();
print connections;

#print "reds",reds
#print "greens",greens
# Use blue band for river
