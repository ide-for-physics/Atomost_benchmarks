# hexagonal path G-M-K-G-A-L-H-A in crystal (reciprocal-lattice) coordinates
import numpy as np, sys
pts={'G':(0,0,0),'M':(0.5,0,0),'K':(1/3,1/3,0),'A':(0,0,0.5),'L':(0.5,0,0.5),'H':(1/3,1/3,0.5)}
path=['G','M','K','G','A','L','H','A']
nseg=int(sys.argv[1]) if len(sys.argv)>1 else 40
mode=sys.argv[2] if len(sys.argv)>2 else 'pw'
out=[]
for a,b in zip(path[:-1],path[1:]):
    pa,pb=np.array(pts[a]),np.array(pts[b])
    for t in np.linspace(0,1,nseg,endpoint=False):
        out.append(pa+(pb-pa)*t)
out.append(np.array(pts[path[-1]]))
if mode=='pw':
    print(len(out))
    for k in out: print(f"{k[0]:.10f} {k[1]:.10f} {k[2]:.10f} 1.0")
else:  # epw filkf: crystal coords with weights
    print(len(out), 'crystal')
    for k in out: print(f"{k[0]:.10f} {k[1]:.10f} {k[2]:.10f} 1.0")
