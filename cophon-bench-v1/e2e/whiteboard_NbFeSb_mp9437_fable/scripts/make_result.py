#!/usr/bin/env python3
"""Build RESULT.json from kernel/Gamma_alphabeta_s.dat, jobs.log, structure_POSCAR and the start/end times.
Usage: make_result.py <mesh string> <start ISO UTC> <end ISO UTC>
"""
import sys, json, numpy as np, datetime as dt
mesh, t0, t1 = sys.argv[1], sys.argv[2], sys.argv[3]
# kernel
fn='kernel/Gamma_alphabeta_s.dat'; modes={}; freq={}; cur=None
for line in open(fn):
    s=line.split()
    if not s or line.lstrip().startswith('#'): continue
    if s[0]=='imode': cur=int(s[2]); freq[cur]=float(s[3]); modes[cur]=[]; continue
    modes[cur].append([float(x) for x in s])
best=None
for m in modes:
    A=np.array(modes[m]); w=A[:,0]; G=A[:,1::2]+1j*A[:,2::2]
    I=np.abs(G).sum(1); sel=w<=6.0+1e-9; i=int(np.argmax(np.where(sel,I,-1)))
    if best is None or I[i]>best[3]: best=(m,freq[m],w[i],I[i])
m,fmev,wpk,Ipk=best
# node hours
nh=0.0
for line in open('jobs.log'):
    if line.startswith('#') or '|' not in line: continue
    nh+=float(line.split('|')[-1])
# cell
L=open('structure_POSCAR').read().splitlines()
cell=[[float(x) for x in L[i].split()] for i in (2,3,4)]
species=[]; 
for sp,n in zip(L[5].split(), L[6].split()): species += [sp]*int(n)
pos=[[float(x) for x in L[8+i].split()[:3]] for i in range(len(species))]
wall=(dt.datetime.fromisoformat(t1)-dt.datetime.fromisoformat(t0)).total_seconds()/3600
res={"schema":"cophon-bench.e.result.v1","material":"NbFeSb_mp9437","kernel_file":"kernel/Gamma_alphabeta_s.dat",
     "peak_ev":round(float(wpk),4),"peak_a2_per_ev":round(float(Ipk),4),"mode_thz":round(fmev/4.135667696,4),
     "mode_irrep":"T2","mesh":mesh,"cell_angstrom":cell,"species":species,"positions_crystal":pos,
     "node_hours":round(nh,3),"wall_hours":round(wall,2),"model_usd":None,"human_touches":0}
json.dump(res,open('RESULT.json','w'),indent=1)
print(json.dumps(res,indent=1))
print(f"# dominant mode {m}: {fmev} meV, peak {wpk} eV, I = {Ipk}")
