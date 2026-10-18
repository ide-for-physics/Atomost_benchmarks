"""Parse Gamma_alphabeta_s.dat (kernel variant EPW) and report per-mode invariants and the global peak.
usage: analyze_kernel.py Gamma_alphabeta_s.dat [emin emax]
Invariant per mode and photon energy: S_s(w) = sum over the 9 Cartesian channels of |Gamma^{ab}_s(w)|  (A^2/eV).
Also reports the Frobenius norm sqrt(sum |Gamma^{ab}|^2) and the largest single channel.
"""
import sys, numpy as np
fn=sys.argv[1]; emin=float(sys.argv[2]) if len(sys.argv)>2 else 0.0; emax=float(sys.argv[3]) if len(sys.argv)>3 else 6.0
modes={}; cur=None
for line in open(fn):
    s=line.split()
    if not s or s[0].startswith('#'): continue
    if s[0]=='imode':
        cur=(int(s[2]),float(s[3])); modes[cur]=[]; continue
    v=[float(x) for x in s]; modes[cur].append(v)
chan=['xx','yy','zz','xy','xz','yz','yx','zx','zy']
best=None
print("mode  w_s(meV)  w_s(THz)   E_peak(eV)  S=sum|G^{ab}|  Frobenius  max|channel|(chan)   at E_peak")
for (im,wmev),rows in modes.items():
    a=np.array(rows); E=a[:,0]; G=a[:,1::2]+1j*a[:,2::2]   # (nE,9)
    absG=np.abs(G); S=absG.sum(1); F=np.sqrt((absG**2).sum(1))
    sel=(E>=emin)&(E<=emax); i=np.argmax(np.where(sel,S,-1))
    j=np.argmax(absG[i])
    print("%4d %9.4f %8.4f   %8.3f   %12.6e %12.6e %12.6e (%s)"%(im,wmev,wmev/4.135667696,E[i],S[i],F[i],absG[i,j],chan[j]))
    if best is None or S[i]>best[0]: best=(S[i],E[i],im,wmev,F[i],G[i])
S,E,im,wmev,F,G=best
print("\nGLOBAL PEAK: mode %d (%.4f meV = %.4f THz) at E = %.3f eV: S = %.6e A^2/eV (Frobenius %.6e)"%(im,wmev,wmev/4.135667696,E,S,F))
print("channels at peak (Re, Im):"); 
for c,g in zip(chan,G): print("  %s  %12.5e %12.5e  |.|=%12.5e"%(c,g.real,g.imag,abs(g)))
