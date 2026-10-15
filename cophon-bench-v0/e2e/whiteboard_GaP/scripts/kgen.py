#!/usr/bin/env python3
"""Generate (a) the full NSCF k-grid in [0,1) crystal coords for EPW, (b) a high-symmetry path for fcc
(reciprocal basis of the POSCAR cell a1=(0,1,1)a/2, a2=(1,0,1)a/2, a3=(1,1,0)a/2) as explicit lists."""
import sys, math
n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
# (a) uniform grid
with open('kgrid_%d.txt' % n, 'w') as f:
    f.write('K_POINTS crystal\n%d\n' % (n**3))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                f.write('%12.8f %12.8f %12.8f 1.0\n' % (i/n, j/n, k/n))
# (b) path. Crystal coords in the POSCAR reciprocal basis b1=(-1,1,1), b2=(1,-1,1), b3=(1,1,-1) (2pi/a)
pts = {'G': (0,0,0), 'X': (0,0.5,0.5), 'W': (0.25,0.5,0.75), 'K': (0.375,0.375,0.75),
       'L': (0.5,0.5,0.5), 'U': (0.25,0.625,0.625)}
def cart(c):  # in units of 2pi/a
    x,y,z = c
    return (-x+y+z, x-y+z, x+y-z)
path = [('G','X'),('X','W'),('W','K'),('K','G'),('G','L'),('L','U'),('U','W'),('W','L'),('L','K'),('U','X')]
dens = 60  # points per unit of 2pi/a
klist = []; labels = []; start = 0.0
for iseg,(a,b) in enumerate(path):
    ca, cb = cart(pts[a]), cart(pts[b])
    L = math.sqrt(sum((cb[i]-ca[i])**2 for i in range(3)))
    npts = max(2, int(round(L*dens)))
    last = (iseg == len(path)-1) or (path[iseg+1][0] != b)   # include endpoint if path breaks here
    labels.append((a, start))
    for m in range(npts + (1 if last else 0)):
        t = m/npts
        c = tuple(pts[a][i] + t*(pts[b][i]-pts[a][i]) for i in range(3))
        klist.append((c, start + t*L))
    if last: labels.append((b, start + L))
    start += L
with open('kpath.txt', 'w') as f:
    f.write('%d crystal\n' % len(klist))
    for c,d in klist:
        f.write('%12.8f %12.8f %12.8f 1.0\n' % c)
with open('kpath_dist.txt', 'w') as f:
    for c,d in klist:
        f.write('%12.8f %12.8f %12.8f %12.8f\n' % (c[0],c[1],c[2],d))
with open('kpath_labels.txt', 'w') as f:
    for l,d in labels: f.write('%s %12.8f\n' % (l,d))
print('grid', n**3, 'path points', len(klist))
