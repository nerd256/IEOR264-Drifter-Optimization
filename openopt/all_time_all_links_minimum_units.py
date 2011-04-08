# -*- coding: utf-8 -*-
 
from FuncDesigner import *
from openopt import MILP 
from numpy import array, zeros; 
import sys;
import time as time_module;

pidx = 0;
paths = [];

fin = open("paths.txt","r");
numlabs = int(fin.readline());

timeH = 0;
for line in fin:
    (pathpx, rest) = line.split(":",1);
    path = [int(i) for i in rest.split(',')];
    
    paths.append(path);
    if len(path) > timeH:
        timeH = len(path);
        
    pidx += 1;
fin.close();

toappend = [];
for path in paths:
    slack = timeH - len(path);
    ptemp = path[:]
    for wait in range(1,slack+1):
        ptemp.insert(0,0);
        toappend.append(ptemp[:]);
       
paths.extend(toappend);
print "Added",len(toappend),"waiting paths."

numpaths = len(paths);
print "Pre-computing over",timeH,"time",numpaths,"paths."
mustpaths = [];
covered = [];
imposs = [];
# find labels with 0 and 1 paths going through
for time in range(0,timeH):
    for lidx in range(0,numlabs):
        cnt = 0;
        lastpidx = 0;
        
        for pidx in range(0,numpaths):
            if time < len(paths[pidx]) and paths[pidx][time] == lidx:
                cnt += 1;
                lastpidx = pidx;
                
        if ( cnt == 0 ):
            covered.append((lidx,time));
            imposs.append((lidx,time));
        elif ( cnt == 1 ):
            if ( lastpidx not in mustpaths ):
                mustpaths.append(lastpidx);
                for link_no in range(0,len(paths[lastpidx])):
                    if (paths[lastpidx][link_no],link_no) not in covered:
                        covered.append((paths[lastpidx][link_no],link_no))

print "Paths ",mustpaths," (%d) must be taken."%(len(mustpaths))
print len(imposs),"labels impossible to satisfy."
print "Total",len(covered),"/",(numlabs * timeH),"labels ignored."
#print covered," labels can be ignored."

rpmap = {};
rpidx = 0;
for pidx in range(0,numpaths):
    if ( pidx not in mustpaths ):
        rpmap[rpidx] = pidx;
        #print rpidx,"->",pidx
        rpidx += 1;
        
rlmap = {};
rlidx = 0;
for time in range(0,timeH):
    for lidx in range(0,numlabs):
        if ( (lidx,time) not in covered ):
            rlmap[rlidx] = (lidx,time);
            #print rlidx,"->",lidx
            rlidx += 1;

optpaths = numpaths - len(mustpaths);
optlabs = numlabs*timeH - len(covered);
print "Optpaths: %d, Optlabs %d"%(optpaths,optlabs)
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
            if ( rlmap[lidx][1] < len(paths[rpmap[pidx]]) and paths[rpmap[pidx]][rlmap[lidx][1]] == rlmap[lidx][0] ):
                A[lidx,pidx] = -1; # everything negated

    b = [-1]*optlabs;


    p = MILP(f=f, lb=lb, ub=ub, A=A, b=b, intVars=intVars, goal='min')
    #r = p.solve('lpSolve')
    curtime = time_module.time();
    r = p.solve('glpk')
    print "Solver done. Took %.5f real time."%(time_module.time()-curtime)
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