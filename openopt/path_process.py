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

colors = [];
for i in range(0,1000):
    colors.append((random()*256,random()*256,random()*256));
colors[0] = (255,0,0);
colors[1] = (0,255,0);
colors[2] = (0,0,255);
colors[3] = (255,255,0);
colors[4] = (0,255,255);
colors[5] = (255,0,255);


def disp_labs():
    global dispimg
    dispimg = Image.new('RGB',img.size,(255,255,255));
    disppx = dispimg.load();
    for y in range(0,img.size[1]):
        for x in range(0,img.size[0]):
            if ( pathpx[x,y][0] != 255 ):
                disppx[x,y] = colors[pathpx[x,y][0]];
    dispimg.show();
   
    

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

def relabel_edge(thelist, old, new):
   for j in range(0,len(thelist)):
        if ( thelist[j][2] == old ):
          thelist[j] = (thelist[j][0],thelist[j][1],new)

gx,gy = greens[0];
i = 0;
pix[gx,gy] = (0,255,0);
edge = [(gx,gy,0)];
newedge = [];
connections = [];
nextlabel = 1;
while edge:
    for (x, y, l) in edge:
        for (s, t) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1),(x-1,y-1)):
            if s >= 0 and t >= 0 and s < img.size[0] and t < img.size[1] and \
                pix[s,t][1] != 255 and pix[s,t][0] == 0:
                pix[s,t] = (0,255,0);
                newedge.append((s, t, l))
                
    edge = []

    p = 0;
    labels_seen = [];
    while newedge:
        (x,y,l) = newedge.pop();

        if ( l in labels_seen ): 
            # already saw this label, but not a part of it, a new edge is born: generate two new labels and assign
            old = l;
            l1 = nextlabel;
            l2 = nextlabel + 1;
            nextlabel += 2;
            # relabel everything from before
            relabel_edge(edge, old, l1);
            
            l = l2; # working from second label now
            connections.append((old,l2));
            connections.append((old,l1)); # split
                    
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
                        if ( ol != l ) :
                            l1 = nextlabel;
                            nextlabel += 1;
                            connections.append((ol,l1)); #join, create new ID and relabel
                            connections.append((l,l1));
                            # relabel everything we've processed so far + the new edge
                            relabel_edge(edge, l, l1);
                            relabel_edge(tocheck, l, l1);
                            relabel_edge(newedge, ol, l1);
                            l = l1;
                            
                            

        p += 1;

    for (x,y,l) in edge:
       pathpx[x,y] = (l,l,l);
    
    #pathimg.save("frames/%04d.png"%i);
    i += 1;
    

#disp_labs();
#dispimg.save("output.png");

totals = 0;
pixcnts = [0]*nextlabel;
for y in range(0,img.size[1]):
    for x in range(0,img.size[0]):
        if pathpx[x,y][0] != 255:
            pixcnts[ pathpx[x,y][0] ] += 1
            totals += 1

   
#for i in range(0,nextlabel):
#    print "Label %d : %d pixels (%.2f%%)" % (i,pixcnts[i],100*pixcnts[i]/float(totals))

# enumerate paths using DFS
connections = sorted(connections);
print connections
visited = [0];
n = 0;
def DFS():
    global visited, n
    l = visited[-1];
    # find adjacent nodes
    adj = [];
    for (l1, l2) in connections:
        if ( l1 == l and not l2 in visited):
            adj.append(l2);
            
    if len(adj) == 0:
        #end of path
        n += 1;
        print visited
        return;
    
    for o in adj:
        visited.append(o);
        DFS();

DFS();

print n,"paths"