"""Build RESULT.json from the converged kernel file + metadata.
usage: make_result.py kernel_file mesh node_hours wall_hours"""
import sys, json, numpy as np
fn, mesh, nh, wh = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
irrep={25.4539:'Eu',25.5857:'Eg',38.6486:'A1g',42.2116:'A2u'}   # DFPT at Gamma, ph.x mode-symmetry analysis (D3d)
modes={}; cur=None
for line in open(fn):
    s=line.split()
    if not s or s[0].startswith('#'): continue
    if s[0]=='imode': cur=(int(s[2]),float(s[3])); modes[cur]=[]; continue
    modes[cur].append([float(x) for x in s])
best=None
for (im,wmev),rows in modes.items():
    a=np.array(rows); E=a[:,0]; S=np.abs(a[:,1::2]+1j*a[:,2::2]).sum(1)
    sel=(E>=0)&(E<=6.0); i=np.argmax(np.where(sel,S,-1))
    if best is None or S[i]>best[0]: best=(S[i],E[i],im,wmev)
S,E,im,wmev=best
key=min(irrep,key=lambda w:abs(w-wmev))
res={"schema":"cophon-bench.e.result.v1","material":"SnS2_mp1170","kernel_file":"kernel/Gamma_alphabeta_s.dat",
 "peak_ev":round(float(E),3),"peak_a2_per_ev":float("%.6g"%S),
 "mode_thz":round(wmev/4.135667696,4),"mode_irrep":irrep[key],"mesh":mesh,
 "cell_angstrom":[[1.8195,-3.15146644,0.0],[1.8195,3.15146644,0.0],[0.0,0.0,5.868]],
 "species":["Sn","S","S"],
 "positions_crystal":[[0.0,0.0,0.0],[0.33333333,0.66666667,0.25418572],[0.66666667,0.33333333,0.74581428]],
 "node_hours":nh,"wall_hours":wh,"model_usd":None,"human_touches":0}
json.dump(res,open('RESULT.json','w'),indent=1); print(json.dumps(res,indent=1))
