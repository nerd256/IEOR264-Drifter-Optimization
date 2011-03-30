# -*- coding: utf-8 -*-
 
from FuncDesigner import *
from openopt import MILP 
from numpy import array, zeros; 

n = 5;
D = 20;
c =  [
    [5, 1.5, 0, 0, 0],
    [1.5, 5, -1, 0, 0],
    [0, 3, 5, 1.5, 0],
    [0, 0, 1.5, 5, 3],
    [0, 0, 0, 1.5, 2]];

# Define some oovars
x = oovar(size=n)
 
# Define objective; sum(a) and a.sum() are same as well as for numpy arrays
obj = sum(dot(c,x));
print obj
# Start point - currently matters only size of variables
startPoint = {x:zeros(n)} # however, using numpy.arrays is more recommended than Python lists
print obj(startPoint)
# Create prob
p = MILP(obj, startPoint, intVars = [x])
 
# Define some constraints
p.constraints = [x.sum() <= D, x >= 0]
 
# Solve
# NOTE: must remove os.close in /usr/local/lib/python2.6/dist-packages/openopt-0.33-py2.6.egg/openopt/solvers/CVXOPT/CVXOPT_LP_Solver.py
r = p.maximize('glpk') # glpk is name of the solver involved, see OOF doc for more arguments

# Decode solution
print('Solution: x = %s' % (str(x(r))))
# Solution: x = [-5.  -4.5]   y = -17.000000  z = 0.000000