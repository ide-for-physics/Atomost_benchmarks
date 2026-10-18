#!/usr/bin/env python3
import sys, re, numpy as np
fn=sys.argv[1]; out=sys.argv[2]
txt=open(fn).read()
blocks=re.split(r'\n\s+k =', txt)[1:]
E=[]
for b in blocks:
    if 'bands (ev)' not in b: continue
    body=b.split('bands (ev):')[1]
    body=re.split(r'highest|occupation numbers|Writing|\n\s*\n\s*\n', body)[0]
    vals=[float(x) for x in re.findall(r'-?\d+\.\d+', body.replace('-',' -'))]
    E.append(vals)
n=min(len(e) for e in E)
E=np.array([e[:n] for e in E])
np.savetxt(out, E, fmt='%10.4f')
print(fn, E.shape)
