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
    #dispimg.show();
   
    

greens = [];
reds = [];

for y in range(0,img.size[1]):
    for x in range(0,img.size[0]):
        if ( pix[x,y][2] < 255 ):
            if ( pix[x,y][0] == 255 ) :
                reds.append((x,y));
            elif ( pix[x,y][1] == 255 ) :
                #print x,y
                greens.append((x,y));
                pix[x,y] = (0,0,0);

            #print x,y,pix[x,y]

def relabel_edge(thelist, old, new):
   for j in range(0,len(thelist)):
        if ( thelist[j][2] == old ):
          thelist[j] = (thelist[j][0],thelist[j][1],new)
          
   for j in range(0,len(red_labels)):
        if ( red_labels[j] == old ): 
            red_labels[j] = new;
            break;


# flood fill heavily modified from http://mail.python.org/pipermail/image-sig/2005-September/003559.html
gx,gy = greens[0];
i = 0;
pix[gx,gy] = (0,255,0);
edge = [(gx,gy,0)];
newedge = [];
connections = [];
red_labels = [];
nextlabel = 1;
while edge:
    for (x, y, l) in edge:
        for (s, t) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1),(x-1,y-1)):
            if s >= 0 and t >= 0 and s < img.size[0] and t < img.size[1] and \
                pix[s,t][2] == 0:
                if ( pix[s,t][1] != 255 ):  
                    if pix[s,t][0] == 255 and not l in red_labels:
                        red_labels.append(l);
                        
                    pix[s,t] = (0,255,0);
                    newedge.append((s, t, l))
                #elif (pathpx[s,t][0] == 255): #uh oh! this has been changed in our run!
                    #figure out label and connect
                    #for (ox,oy,ol) in newedge:
                    #    if (s==ox and y == oy and (ol,l) not in connections and (l,ol) not in connections):
                            #connections.append((ol,l));
                            #connections.append((l,ol));
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
            for (mx, my) in ((cx+1, cy), (cx-1, cy), (cx,cy+1), (cx, cy-1), (cx+1,cy+1),(cx-1,cy+1),(cx+1,cy-1),(cx-1,cy-1)):
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
    
    disp_labs();
    dispimg.save("frames/%04d.png"%i);
    i += 1;
    

totals = 0;
pixcnts = [0]*nextlabel;
for y in range(0,img.size[1]):
    for x in range(0,img.size[0]):
        if pathpx[x,y][0] != 255:
            pixcnts[ pathpx[x,y][0] ] += 1
            totals += 1
changed = True
while changed:
    #print connections
    changed = False
    for i in range(0,nextlabel):
        #print "Label %d : %d pixels (%.2f%%)" % (i,pixcnts[i],100*pixcnts[i]/float(totals))
        if ( pixcnts[i] == 0 ):
            #remove
            to = [];
            fr = [];
            for (l1,l2) in connections[:]:
                #print (l1,l2)
                if (l1 == i):
                    to.append(l2);
                    connections.remove((l1,l2))
                    changed = True;
                elif ( l2 == i):
                    fr.append(l1);
                    connections.remove((l1,l2))
                    changed = True;
                
            for f in fr:
                for t in to:
                    if (f,t) not in connections:
                        connections.append((f,t));


#rename unused labels
fidx = 0;
tidx = 0;
while fidx < nextlabel:
    if ( pixcnts[fidx] > 0 ):
        fidx += 1;
        tidx += 1;
    else:
        fidx += 1;
    
    if ( fidx != tidx ):
        #relabel label png
        for y in range(0,img.size[1]):
            for x in range(0,img.size[0]):
                if ( pathpx[x,y][0] == fidx ):
                    pathpx[x,y] = (tidx,tidx,tidx);
        
        #relabel all connections
        for cidx in range(0,len(connections)):
            if ( connections[cidx][0] == fidx):
                connections[cidx] = (tidx, connections[cidx][1]);
            elif ( connections[cidx][1] == fidx):
                connections[cidx] = (connections[cidx][0],tidx);
                
        #relabel red labels
        for ridx in range(0,len(red_labels)):
            if ( red_labels[ridx] == fidx ):
                red_labels[ridx] = tidx;
    
nextlabel = tidx;

disp_labs();
dispimg.save("output.png");
pathimg.save("labelled.png");
print "Total labels are: ",nextlabel
print "Sink labels are: ",red_labels

# enumerate paths using DFS
connections = sorted(connections);
print connections
print "Total connections:",len(connections)
paths = [];
visited = [0];
allvisited = [0];
n = 0;
totpix = pixcnts[0];
def DFS():
    global visited, n, allvisited, totpix
    l = visited[-1];
    # find adjacent nodes
    adj = [];
    for (l1, l2) in connections:
        if ( l1 == l and not l2 in visited):
            adj.append(l2);
        #elif ( l2 == l and not l1 in visited):
        #    adj.append(l1);
    
    if len(adj)==0 and l not in red_labels:
        # try "plowing through"
        for (l1,l2) in connections:
            if ( l2 == l and l1 not in visited ):
               adj.append(l1);
    
    if l in red_labels:
        #end of path
        n += 1;
        paths.append((visited[:],totpix));
        #print visited,totpix
        return;
    
    for o in adj:
        visited.append(o);
        totpix += pixcnts[o];
        allvisited.append(o);
        DFS();
        totpix -= pixcnts[o];
        visited.remove(o);

DFS();

print n,"total paths, ",len(paths),"paths to sink"
bestpix = 0;
bestpath = [];
for (path,pix) in paths:
    if bestpix < pix:
        bestpix = pix;
        bestpath = path;
        
print "Best path %d pixels: " %bestpix,bestpath

print "Writing paths.txt"
fout = open('paths.txt','w');
fout.write("%d\n"%nextlabel);
for (path,pix) in paths:
    fout.write("%d:"%pix);
    fout.write(",".join(str(i) for i in path));
    fout.write("\n");
fout.close()
print "Done."
