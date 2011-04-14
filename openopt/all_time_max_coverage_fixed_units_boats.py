# -*- coding: utf-8 -*-
 
from FuncDesigner import *
from openopt import MILP 
from numpy import array, zeros; 
import time as time_module;

NUMDRIFTERS = 40;
TIME = 50;
BOATCOST = 10;
BOATTIME = 10;

pidx = 0;
paths = [];

fin = open("paths.txt","r");numlabs = int(fin.readline());

for line in fin:
    (pathpx, rest) = line.split(":",1);
    path = [int(i) for i in rest.split(',')];
    
    paths.append(path);

    pidx += 1;
fin.close();

fin = open("labs.txt","r");
labpx = [];
for line in fin:
    labpx.append(int(line));
fin.close();

toappend = [];
for path in paths:
    slack = TIME - len(path);
    ptemp = path[:]
    for wait in range(1,slack+1):
        ptemp.insert(0,0);
        toappend.append(ptemp[:]);
       
paths.extend(toappend);
print "Added",len(toappend),"waiting paths."

numpaths = len(paths);
print "Pre-computing over",TIME,"time",numpaths,"paths."

mustpaths = [];
imposs = [];
# find labels with 0 and 1 paths going through
for time in range(0,TIME):
    for lidx in range(0,numlabs):
        cnt = 0;
        lastpidx = 0;
        
        for pidx in range(0,numpaths):
            if time < len(paths[pidx]) and paths[pidx][time] == lidx:
                cnt += 1;
                lastpidx = pidx;
                
        if ( cnt == 0 ):
            imposs.append((lidx,time));

print len(imposs),"labels impossible to satisfy."
print "Total",len(imposs),"/",(numlabs * TIME),"labels ignored."

rlmap = {};
rlidx = 0;
labpx_pruned = []
labpx_tot = 0;
for time in range(0,TIME):
    for lidx in range(0,numlabs):
        if ( (lidx,time) not in imposs ):
            rlmap[rlidx] = (lidx,time);
            labpx_pruned.append(labpx[lidx]);
            labpx_tot += labpx[lidx];
            #print rlidx,"->",lidx
            rlidx += 1;

optlabs = numlabs*TIME - len(imposs);
optneeded_paths = 0;
print "optlabs: %d numpaths: %d totpx: %d"%(optlabs,numpaths,labpx_tot)
if ( optlabs > 0 ):
    # F = sum(x_i) i from 0 to numpaths
    f = [0]*numpaths;
    f.extend(labpx_pruned);
    f.extend([BOATCOST]*TIME);
    intVars = range(0,numpaths + optlabs + TIME); # all integer variables

    lb = array([0.0]*len(intVars));
    ub = array([1.0]*len(intVars)); # assume binary variables ( wouldn't go down same path twice / can't make a node double count)
    
    # Constraints:
    # Ax_paths >= x_labs --> -Ax_paths + x_labs <= 0
    # --> [-A I 0] [x_paths <= 0
    #            x_labs
    #            x_boat]
    
    # Max number of drifters
    # --> [1 1 1 1 1 1...] *x_paths = MAX
    
    # Boat travel time
    # --> [1 1 1 1 1 0 0 ...] * x_boat <= 1
    # AND [0 1 1 1 1 1 0....] * x_boat <= 1
    # AND [0 0 1 1 1 1 1... ] etc...
    
    
    A = zeros((optlabs + 1 + (TIME-BOATTIME+1), numpaths + optlabs + TIME))
    print "Making constraints: Label satisfaction"
    for pidx in range(0,numpaths):
        for lidx in range(0,optlabs):
            if ( rlmap[lidx][1] < len(paths[pidx]) and paths[pidx][rlmap[lidx][1]] == rlmap[lidx][0] ):
                A[lidx,pidx] = -1; # everything negated
        
        A[optlabs,pidx] = 1;
        
    b = [0]*optlabs;

    print "Making constraints: Number of drifters"
    # number of units allowed
    for lidx in range(0,optlabs):
        A[lidx,lidx+numpaths] = 1;   
          
    b = b + [NUMDRIFTERS];   

    print "Making constraints: Boat trip length"
    # boat use constraints
    for ridx in range(0,TIME-BOATTIME+1):
        for cidx in range(ridx,ridx+BOATTIME):
            A[optlabs + 1 + ridx,numpaths+optlabs+cidx] = 1;
            
    b = b + [1]*(TIME-BOATTIME+1);

    p = MILP(f=f, lb=lb, ub=ub, A=A, b=b, intVars=intVars, goal='max')
    #r = p.solve('lpSolve')
    curtime = time_module.time();
    r = p.solve('cplex')
    print "Solver done. Took %.5f real time."%(time_module.time()-curtime)
    optlabels_hit = r.ff

# Decode solution
labs_got = [];
if ( optlabs > 0 ):
    for lidx in range(0,optlabs):
        if ( r.xf[lidx+numpaths] == 1 ):
            labs_got.append(rlmap[lidx]);
            
taken = [];
if ( optlabs > 0 ):
    for pidx in range(0,numpaths):
        if ( r.xf[pidx] == 1 ):
            taken.append(pidx);

boat_taken = [];
if ( optlabs > 0 ):
    for bidx in range(0,TIME):
        if ( r.xf[bidx + numpaths + optlabs] == 1 ):
            boat_taken.append(bidx);
    
print 'Taken paths:',taken
print "Boat trip taken at t=",boat_taken
print "Writing output"
fout = open("taken_paths.txt","w");
for pidx in taken:
    fout.write(",".join(str(i) for i in paths[pidx]));
    fout.write("\n");
fout.close();
print "Done"