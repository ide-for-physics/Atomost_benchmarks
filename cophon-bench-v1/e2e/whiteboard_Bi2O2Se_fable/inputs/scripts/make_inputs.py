#!/usr/bin/env python3
"""Build bands.in and nscf.in from scf.in (same cell/positions/species), appending explicit k lists.
Usage: make_inputs.py nbnd
"""
import sys, re
nbnd = int(sys.argv[1])
scf = open('scf.in').read()
head, kblock = scf.split('K_POINTS')
def mk(calc, outdir, extra_sys, extra_el, kfile):
    t = head.replace("calculation = 'scf'", "calculation = '%s'" % calc)
    t = t.replace("outdir = './tmp'", "outdir = '%s'" % outdir)
    t = re.sub(r"  nbnd = \d+\n", "  nbnd = %d\n%s" % (nbnd, extra_sys), t)
    t = t.replace("&electrons\n", "&electrons\n" + extra_el)
    t = t.replace("  tprnfor = .true.\n  tstress = .true.\n", "")
    return t + open(kfile).read()
open('bands.in', 'w').write(mk('bands', './tmp_bands', '', "  diago_thr_init = 5.0d-6\n  diago_full_acc = .true.\n", 'path_pw_explicit.txt'))
open('nscf.in', 'w').write(mk('nscf', './tmp_nscf', "  nosym = .true.\n  noinv = .true.\n",
                              "  diago_thr_init = 5.0d-6\n  diago_full_acc = .true.\n", 'nscf_kpts.txt'))
print('wrote bands.in, nscf.in with nbnd =', nbnd)
