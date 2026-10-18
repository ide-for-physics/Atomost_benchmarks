#!/usr/bin/env python3
"""Fill the EPW templates. Usage:
  fill_epw.py main  VARIANT            -> epw_main.in   (wannierize + coarse e-ph + band_plot + epwwrite)
  fill_epw.py kern  VARIANT NKF        -> epw_kern<NKF>.in
  fill_epw.py job   NKF PART NT CPT WALL -> job_kern<NKF>.sbatch
VARIANT in {v1, v2b, v6}. Fermi level = mid-gap of the DFT bands (VBM 10.674, CBM 10.998 eV).
"""
import sys
EF = '%.4f' % ((10.674 + 10.998) / 2)
V = {
 'v1':  dict(NBNDSUB='20', DISWINMAX='18.7', DISFROZMAX='16.2',
             PROJ="  proj(1)     = 'Bi:s;p'\n  proj(2)     = 'O:s;p'\n  proj(3)     = 'Se:s;p'"),
 'v1b': dict(NBNDSUB='20', DISWINMAX='20.7', DISFROZMAX='15.7',
             PROJ="  proj(1)     = 'Bi:s;p'\n  proj(2)     = 'O:s;p'\n  proj(3)     = 'Se:s;p'"),
 'v2b': dict(NBNDSUB='30', DISWINMAX='28.0', DISFROZMAX='19.6',
             PROJ="  proj(1)     = 'Bi:s;p;d'\n  proj(2)     = 'O:s;p'\n  proj(3)     = 'Se:s;p'"),
 'v6':  dict(NBNDSUB='30', DISWINMAX='28.0', DISFROZMAX='19.6',
             PROJ="  scdm_proj   = .true.\n  auto_projections = .true.\n  scdm_entanglement = 'erfc'\n  scdm_mu     = 18.7\n  scdm_sigma  = 2.0"),
}
mode = sys.argv[1]
if mode == 'main':
    v = V[sys.argv[2]]
    t = open('epw_main.in.template').read()
    for k, val in v.items(): t = t.replace('@%s@' % k, val)
    t = t.replace('@EFERMI@', EF)
    if sys.argv[2] not in ('v1', 'v1b'):   # looser tolerances for the 30-WF sets (slow disentanglement)
        t = t.replace("num_iter    = 2000", "num_iter    = 600").replace("dis_num_iter = 2000", "dis_num_iter = 800")
        t = t.replace("dis_conv_tol = 1.0d-11", "dis_conv_tol = 1.0d-9").replace("conv_tol = 1.0d-11", "conv_tol = 1.0d-9")
    open('epw_main.in', 'w').write(t); print('wrote epw_main.in for', sys.argv[2])
elif mode == 'kern':
    v = V[sys.argv[2]]; nkf = sys.argv[3]
    t = open('epw_kern.in.template').read().replace('@NBNDSUB@', v['NBNDSUB']).replace('@EFERMI@', EF).replace('@NKF@', nkf)
    open('epw_kern%s.in' % nkf, 'w').write(t); print('wrote epw_kern%s.in' % nkf)
elif mode == 'job':
    nkf, part, nt, cpt, wall = sys.argv[2:7]
    t = open('job_kern.sbatch.template').read()
    for k, val in dict(NKF=nkf, PART=part, NT=nt, CPT=cpt, WALL=wall).items(): t = t.replace('@%s@' % k, val)
    open('job_kern%s.sbatch' % nkf, 'w').write(t); print('wrote job_kern%s.sbatch' % nkf)
