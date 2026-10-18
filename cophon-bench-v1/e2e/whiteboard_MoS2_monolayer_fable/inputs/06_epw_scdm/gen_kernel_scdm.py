#!/usr/bin/env python3
"""gen_kernel_scdm.py NKF [...] : kernel inputs for the stage-2 SCDM 20-WF model (sensitivity test). Run inside 06_kernel_scdm/."""
import os, sys
tmpl = open('../05_kernel/epw2_kernel.in.template').read()
subs = {'@NW@': '20', '@EXCL@': '1-6', '@WMIN@': '-7.0', '@WMAX@': '12.0', '@FMIN@': '-7.0', '@FMAX@': '7.0',
        '@PROJ@': "  scdm_proj   = .true.\n  auto_projections = .true.\n  scdm_entanglement = 'erfc'\n  scdm_mu     = 7.0\n  scdm_sigma  = 2.0",
        '@EF@': '0.3675'}
files = ['epwdata.fmt', 'crystal.fmt', 'vmedata.fmt', 'dmedata.fmt', 'wigner.fmt', 'mos2.ukk', 'mos2.kgmap', 'mos2.kmap',
         'mos2_wsvec.dat', 'mos2.chk', 'mos2.nnkp', 'mos2_hr.dat', 'mos2.bvec']
for n in sys.argv[1:]:
    d = 'k%s' % n
    os.makedirs(d, exist_ok=True)
    s = tmpl
    for k, v in subs.items():
        s = s.replace(k, v)
    s = s.replace('@NKF@', n).replace("'../../03_nscf/tmp'", "'../../03_nscf/tmp_scdm'")
    open(os.path.join(d, 'epw_k%s.in' % n), 'w').write(s)
    for f in files:
        if os.path.exists(os.path.join('..', '06_epw_scdm', f)) and not os.path.exists(os.path.join(d, f)):
            os.symlink(os.path.join('..', '..', '06_epw_scdm', f), os.path.join(d, f))
    print('prepared', d)
