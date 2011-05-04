# -*- coding: utf-8 -*-
 
from FuncDesigner import *
from openopt import MILP 
from numpy import array, zeros; 

pidx = 0;
paths = [];

fin = open("paths.txt","r");
numlabs = int(fin.readline());


for line in fin:
    (pathpx, rest) = line.split(":",1);
    path = [int(i) for i in rest.split(',')];
    
    paths.append(path);
    
    pidx += 1;
fin.close();

numpaths = len(paths);

mustpaths = [];
covered = [];
imposs = [];
# find labels with 0 and 1 paths going through
for lidx in range(0,numlabs):
    cnt = 0;
    lastpidx = 0;
    for pidx in range(0,numpaths):
        if lidx in paths[pidx]:
            cnt += 1;
            lastpidx = pidx;
            
    if ( cnt == 0 ):
        covered.append(lidx);
        imposs.append(lidx);
    elif ( cnt == 1 ):
        if ( lastpidx not in mustpaths ):
            mustpaths.append(lastpidx);
            for l in paths[lastpidx]:
                if l not in covered:
                    covered.append(l)

print "Paths ",mustpaths,"(%d/%d) must be taken."%(len(mustpaths),numpaths)
print "Labels",imposs,"(%d/%d) impossible to satisfy."%(len(imposs),numlabs)
print covered," (%d) labels can be ignored."%(len(covered))

rpmap = {};
rpidx = 0;
for pidx in range(0,numpaths):
    if ( pidx not in mustpaths ):
        rpmap[rpidx] = pidx;
        #print rpidx,"->",pidx
        rpidx += 1;
        
rlmap = {};
rlidx = 0;
for lidx in range(0,numlabs):
    if ( lidx not in covered ):
        rlmap[rlidx] = lidx;
        #print rlidx,"->",lidx
        rlidx += 1;        

optpaths = numpaths - len(mustpaths);
optlabs = numlabs - len(covered);
optneeded_paths = 0;
if ( optpaths > 0 and optlabs > 0):
    # F = sum(x_i) i from 0 to numpaths
    f = [1]*optpaths; 
    intVars = range(0,optpaths); # all integer variables

    lb = array([0.0]*optpaths);
    ub = array([1.0]*optpaths); # assume binary variables ( wouldn't go down same path twice )
    A = zeros((optlabs, optpaths))

    for pidx in range(0,optpaths):
        for lidx in range(0,optlabs):
            if ( rlmap[lidx] in paths[rpmap[pidx]] ):
                A[lidx,pidx] = -1; # everything negated

    b = [-1]*optlabs;


    p = MILP(f=f, lb=lb, ub=ub, A=A, b=b, intVars=intVars, goal='min')
    #r = p.solve('lpSolve')
    r = p.solve('glpk')
    optneeded_paths = r.ff

# Decode solution
print 'Units needed:', len(mustpaths)+optneeded_paths
taken = mustpaths;
if ( optlabs > 0 ):
    for pidx in range(0,optpaths):
        if ( r.xf[pidx] == 1 ):
            taken.append(rpmap[pidx]);
        
print 'Taken paths:',taken
print "Writing output"
fout = open("taken_paths.txt","w");
for pidx in taken:
    fout.write(",".join(str(i) for i in paths[pidx]));
    fout.write("\n");
fout.close();
print "Done"