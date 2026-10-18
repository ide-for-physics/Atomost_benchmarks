#!/usr/bin/env python3
"""Compare kernel files from different fine meshes: per-mode invariant spectra I_s(w) and peak values."""
import sys, numpy as np
def load(fn):
    modes={}; cur=None
    for line in open(fn):
        s=line.split()
        if not s or line.lstrip().startswith('#'): continue
        if s[0]=='imode': cur=int(s[2]); modes[cur]=[]; continue
        modes[cur].append([float(x) for x in s])
    out={}
    for m in modes:
        A=np.array(modes[m]); out[m]=(A[:,0], A[:,1::2]+1j*A[:,2::2])
    return out
files=sys.argv[1:]
data=[load(f) for f in files]
ref=data[-1]
print("# reference =", files[-1])
for f,d in zip(files[:-1],data[:-1]):
    print(f"## {f}")
    for m in sorted(d):
        w,G=d[m]; w2,G2=ref[m]
        I=np.abs(G).sum(1); I2=np.abs(G2).sum(1)
        i=np.argmax(I); i2=np.argmax(I2)
        # smoothed comparison with a 0.05 eV box to reduce noise sensitivity
        k=5; Is=np.convolve(I,np.ones(k)/k,'same'); I2s=np.convolve(I2,np.ones(k)/k,'same')
        print(f"mode {m}: peak {w[i]:.2f} eV I={I[i]:.3f} | ref peak {w2[i2]:.2f} eV I={I2[i2]:.3f} | dPeak={100*(I[i]/I2[i2]-1):+.1f}%  max|dI|/Imax={np.abs(I-I2).max()/I2.max():.3f}  (0.05 eV-smoothed: {np.abs(Is-I2s).max()/I2s.max():.3f})")
