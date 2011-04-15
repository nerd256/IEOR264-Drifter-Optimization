# -*- coding: utf-8 -*-
 
from FuncDesigner import *
from openopt import MILP 
from numpy import array, zeros; 
import time as time_module;

NUMDRIFTERS = 40;
TIME = 200;
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

boattrips = [];
boatoptstart = [];
boatends = [[] for i in range(TIME/BOATTIME/2)];
numpaths = 0;
for bidx in range(0,TIME/BOATTIME/2):
    btime = bidx * BOATTIME * 2;
    #print "Boat time:",btime
    boatl = [];
    boatoptstart.append(numpaths);
    for pidx in range(0,len(paths)):
        endt = btime + len(paths[pidx]);
        if ( endt < TIME ):
            boatl.append(pidx);
            
            idxend = int(0.9999 + (endt + BOATTIME) / BOATTIME / 2);
            
            if ( idxend < len(boatends) ):
                boatends[ idxend ].append(numpaths);
               
            numpaths += 1;
            
    boattrips.append(boatl);

print "Pre-computing over",TIME,"time",numpaths,"paths."

mustpaths = [];
imposs = [];
# find labels with 0 and 1 paths going through
for time in range(0,TIME):
    for lidx in range(0,numlabs):
        cnt = 0;
        lastpidx = 0;
        
        for bidx in range(0,len(boattrips)):
            btime = bidx * BOATTIME * 2;
            if btime > time: break;
            for pidx in boattrips[bidx]:
                if time-btime < len(paths[pidx]) and paths[pidx][time-btime] == lidx:
                    cnt += 1;
                    break;
                
            if cnt > 0: break;
            
        if ( cnt == 0 ):
            imposs.append((lidx,time));

print len(imposs),"labels impossible to satisfy."
print "Total",len(imposs),"/",(numlabs * TIME),"labels ignored."

rlmap = [];
rlidx = 0;
labpx_pruned = []
labpx_tot = 0;
for time in range(0,TIME):
    for lidx in range(0,numlabs):
        if ( (lidx,time) not in imposs ):
            rlmap.append((lidx,time));
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
    intVars = range(0,numpaths + optlabs); # all integer variables

    lb = array([0.0]*len(intVars));
    ub = array([1.0]*len(intVars)); # assume binary variables ( wouldn't go down same path twice / can't make a node double count)
    
    # Constraints:
    # Ax_paths >= x_labs --> -Ax_paths + x_labs <= 0
    # --> [-A I] [x_paths <= 0
    #            x_labs]
    
    # Max number of drifters released at a given time
    # paths starting at boattrip_i <= paths which ended between previous boat trip
    # 
    
    
    A = zeros((optlabs + (TIME/BOATTIME/2), numpaths + optlabs))
    print "Making constraints: Label satisfaction"
    pathno = 0;
    for bidx in range(0,len(boattrips)):
        btime = bidx * BOATTIME * 2;
        for ppidx in range(0,len(boattrips[bidx])):
            for lidx in range(0,optlabs):
                rtime = rlmap[lidx][1] - btime
                if (  rtime >= 0 and rtime < len(paths[boattrips[bidx][ppidx]]) and paths[boattrips[bidx][ppidx]][rtime] == rlmap[lidx][0] ):
                    A[lidx,boatoptstart[bidx] + ppidx] = -1; # everything negated
            
    for lidx in range(0,optlabs):
        A[lidx,lidx+numpaths] = 1;   
        
    b = [0]*optlabs;

    print "Making constraints: Number of drifters"
    # number of units allowed
    # first trip is free
    b = b + [NUMDRIFTERS];
    for pidx in range(0,len(boattrips[0])):
        A[optlabs,pidx] = 1;
            
    # [mask of paths starting at bidx] * x_paths <= [mask of paths ending for bidx] * x_paths
    for bidx in range(1, TIME/BOATTIME/2):
        for pidx in range(0,len(boattrips[bidx])):
            A[optlabs+ bidx,boatoptstart[bidx] + pidx] = 1;
    
        
        for pidx in boatends[bidx]:
            A[optlabs+ bidx,pidx] = -1;
          
    b = b + [0]*(TIME/BOATTIME/2-1);

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
            

paths_taken = [];
boat_carrying = [0]*(TIME/BOATTIME/2);
if ( optlabs > 0 ):
    for bidx in range(0,len(boattrips)):
        print "Boat",bidx,
        for ppidx in range(0,len(boattrips[bidx])):
            if ( r.xf[ boatoptstart[bidx] + ppidx ] == 1):
                paths_taken.append((bidx,paths[boattrips[bidx][ppidx]]));
                boat_carrying[bidx] += 1;
        print " deployed ",boat_carrying[bidx]
    
   
#print 'Taken paths:',paths_taken;
print "Writing output"
fout = open("boat_paths.txt","w");
fout.write("%d\n"%TIME);
fout.write("%d\n"%BOATTIME);
for (bidx,path) in paths_taken:
    fout.write("%d;"%bidx);
    fout.write(",".join(str(i) for i in path));
    fout.write("\n");
fout.close();
print "Done"