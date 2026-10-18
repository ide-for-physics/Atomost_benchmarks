#!/usr/bin/env python3
"""gen_kernel.py NKF [NKF ...] : create k<NKF>/ directories with the EPW kernel input (epwread) and links to the
Wannier-representation files written by the Wannierization run in ../04_epw. Run inside 05_kernel/."""
import os, sys
tmpl = open('epw2_kernel.in.template').read()
subs = {'@NW@': '11', '@EXCL@': '1-6, 18-40', '@WMIN@': '-7.0', '@WMAX@': '4.60', '@FMIN@': '-7.0', '@FMAX@': '4.60',
        '@PROJ@': "  proj(1)     = 'Mo:d'\n  proj(2)     = 'S:p'", '@EF@': '0.3675'}
files = ['epwdata.fmt', 'crystal.fmt', 'vmedata.fmt', 'dmedata.fmt', 'wigner.fmt', 'mos2.ukk', 'mos2.kgmap', 'mos2.kmap',
         'mos2_wsvec.dat', 'mos2.chk', 'mos2.nnkp', 'mos2_hr.dat', 'mos2.bvec']
for n in sys.argv[1:]:
    d = 'k%s' % n
    os.makedirs(d, exist_ok=True)
    s = tmpl
    for k, v in subs.items():
        s = s.replace(k, v)
    s = s.replace('@NKF@', n)
    # the kernel runs live one level deeper than 04_epw: fix the relative paths to the NSCF outdir and the dvscf dir
    s = s.replace("'../03_nscf/tmp'", "'../../03_nscf/tmp'").replace("'../02_ph/save'", "'../../02_ph/save'")
    open(os.path.join(d, 'epw_k%s.in' % n), 'w').write(s)
    for f in files:
        src = os.path.join('..', '..', '04_epw', f)
        dst = os.path.join(d, f)
        if os.path.exists(os.path.join('..', '04_epw', f)) and not os.path.exists(dst):
            os.symlink(src, dst)
    print('prepared', d)
