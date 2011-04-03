# -*- coding: utf-8 -*-
 
from FuncDesigner import *
from openopt import MILP 
from numpy import array, zeros; 

NUMDRIFTERS = 3;

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
        imposs.append(lidx);

print "Labels",imposs,"impossible to satisfy and are ignored."

rlmap = {};
rlidx = 0;
for lidx in range(0,numlabs):
    if ( lidx not in imposs ):
        rlmap[rlidx] = lidx;
        #print rlidx,"->",lidx
        rlidx += 1;        

optlabs = numlabs - len(imposs);
optneeded_paths = 0;
if ( optlabs > 0 ):
    # F = sum(x_i) i from 0 to numpaths
    f = [0]*numpaths;
    f.extend([1]*optlabs);
    intVars = range(0,numpaths + optlabs); # all integer variables

    lb = array([0.0]*len(intVars));
    ub = array([1.0]*len(intVars)); # assume binary variables ( wouldn't go down same path twice / can't make a node double count)
    
    # Constraints:
    # Ax_paths >= x_labs --> -Ax_paths + x_labs <= 0
    # --> [-A I] [x_paths <= 0
    #            x_labs]
    
    # Max number of drifters
    # --> [1 1 1 1 1 1...] *x_paths = MAX
    
    A = zeros((optlabs + 1, numpaths + optlabs))

    for pidx in range(0,numpaths):
        for lidx in range(0,optlabs):
            if ( rlmap[lidx] in paths[pidx] ):
                A[lidx,pidx] = -1; # everything negated
        
        A[optlabs,pidx] = 1;

    for lidx in range(0,optlabs):
        A[lidx,lidx+numpaths] = 1;   

    b = [0]*optlabs + [NUMDRIFTERS];   

    p = MILP(f=f, lb=lb, ub=ub, A=A, b=b, intVars=intVars, goal='max')
    #r = p.solve('lpSolve')
    r = p.solve('cplex')
    optlabels_hit = r.ff

# Decode solution
labs_got = [];
if ( optlabs > 0 ):
    for lidx in range(0,optlabs):
        if ( r.xf[lidx+numpaths] == 1 ):
            labs_got.append(rlmap[lidx]);
            
print 'Labels satisfied:',labs_got
print 'Total Labels satisfied:',optlabels_hit

taken = [];
if ( optlabs > 0 ):
    for pidx in range(0,numpaths):
        if ( r.xf[pidx] == 1 ):
            taken.append(pidx);
        
print 'Taken paths:',taken
print "Writing output"
fout = open("taken_paths.txt","w");
for pidx in taken:
    fout.write(",".join(str(i) for i in paths[pidx]));
    fout.write("\n");
fout.close();
print "Done"