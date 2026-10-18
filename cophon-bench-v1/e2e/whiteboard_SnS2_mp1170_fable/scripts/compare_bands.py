"""Compare DFT bands (bands.x filband format) with EPW/Wannier band.eig along the same k-path.
usage: compare_bands.py bands_dft.dat band.eig nexclude_low evbm ewin_top [out.dat]
  nexclude_low : number of lowest DFT bands excluded from Wannierization
  evbm         : DFT valence band maximum (eV); ewin_top: compare bands with DFT energy <= ewin_top (eV)
"""
import sys, re, numpy as np
def read_plot(fn):
    txt=open(fn).read()
    m=re.search(r'nbnd=\s*(\d+),\s*nks=\s*(\d+)',txt); nb,nk=int(m.group(1)),int(m.group(2))
    toks=txt[m.end():].split(); toks=[t for t in toks if t!='/']
    v=np.array([float(t) for t in toks]); v=v.reshape(nk,3+nb)
    return v[:,:3], v[:,3:]
kd,ed=read_plot(sys.argv[1]); kw,ew=read_plot(sys.argv[2])
nex=int(sys.argv[3]); evbm=float(sys.argv[4]); etop=float(sys.argv[5])
assert kd.shape[0]==kw.shape[0], (kd.shape,kw.shape)
ed=ed[:,nex:]; nbw=ew.shape[1]; ed=ed[:,:nbw]
mask=ed<=etop
diff=(ew-ed)[mask]
vmask=mask&(ed<=evbm+1e-3); cmask=mask&(ed>evbm+1e-3)
def stats(m):
    d=(ew-ed)[m]; return np.sqrt(np.mean(d**2))*1e3, np.max(np.abs(d))*1e3, m.sum()
print("window: DFT bands up to %.3f eV (VBM=%.3f); nk=%d, nbnd_wannier=%d"%(etop,evbm,kd.shape[0],nbw))
for name,m in (("all bands in window",mask),("valence",vmask),("conduction",cmask)):
    r,mx,n=stats(m); print("%-22s RMS = %7.3f meV   max = %7.3f meV   (N=%d)"%(name,r,mx,n))
# per-band summary
for ib in range(nbw):
    m=mask[:,ib]
    if m.sum()==0: continue
    d=(ew[:,ib]-ed[:,ib])[m]
    print("band %2d  Emin=%8.3f Emax=%8.3f  RMS=%7.3f meV max=%7.3f meV"%(ib+1+nex,ed[:,ib].min(),ed[:,ib].max(),np.sqrt(np.mean(d**2))*1e3,np.abs(d).max()*1e3))
if len(sys.argv)>6:
    with open(sys.argv[6],'w') as f:
        f.write("# ik  kx ky kz (cart 2pi/a)  then DFT bands (eV) then Wannier bands (eV)\n")
        for i in range(kd.shape[0]):
            f.write("%4d %10.6f %10.6f %10.6f "%(i,*kd[i])+" ".join("%12.6f"%x for x in ed[i])+"   "+" ".join("%12.6f"%x for x in ew[i])+"\n")
