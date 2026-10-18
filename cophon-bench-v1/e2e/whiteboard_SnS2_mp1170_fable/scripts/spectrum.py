"""Print S_s(E) = sum_ab |Gamma^{ab}_s(E)| for every optical mode on a coarse energy grid, plus the fine structure near the global peak.
usage: spectrum.py Gamma_alphabeta_s.dat [step_eV] [window_eV]"""
import sys, numpy as np
fn=sys.argv[1]; step=float(sys.argv[2]) if len(sys.argv)>2 else 0.2; win=float(sys.argv[3]) if len(sys.argv)>3 else 0.3
modes={}; cur=None
for line in open(fn):
    s=line.split()
    if not s or s[0].startswith('#'): continue
    if s[0]=='imode': cur=(int(s[2]),float(s[3])); modes[cur]=[]; continue
    modes[cur].append([float(x) for x in s])
S={}; E=None
for key,rows in modes.items():
    a=np.array(rows); E=a[:,0]; S[key]=np.abs(a[:,1::2]+1j*a[:,2::2]).sum(1)
keys=list(S); print("E(eV) "+" ".join("m%d(%.1fmeV)"%(k[0],k[1]) for k in keys))
sel=np.isclose((E/step)%1,0,atol=1e-6)|np.isclose((E/step)%1,1,atol=1e-6)
for i in np.where(sel)[0]: print("%5.2f "%E[i]+" ".join("%12.4e"%S[k][i] for k in keys))
tot=np.max(np.array([S[k] for k in keys]),axis=0); i0=np.argmax(tot); kbest=max(keys,key=lambda k:S[k][i0])
print("\nglobal peak: mode %d at %.3f eV, S=%.5e ; fine structure +-%.2f eV:"%(kbest[0],E[i0],tot[i0],win))
for i in range(max(0,i0-int(win/0.01)),min(len(E),i0+int(win/0.01)+1),2): print("  %5.2f %12.5e"%(E[i],S[kbest][i]))
