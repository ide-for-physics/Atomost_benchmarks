#!/bin/bash
# collect ph.x outputs for EPW 7.5 (layout of EPW's pp.py for a 1x1x1 q mesh)
mkdir -p save/nfs.phsave
cp tmp/_ph0/nfs.dvscf1 save/nfs.dvscf_q1
cp tmp/_ph0/nfs.phsave/patterns.1.xml save/nfs.phsave/patterns.1.xml
cp nfs.dyn1 save/nfs.dyn_q1
cp nfs.dyn0 save/nfs.dyn0
ls -laR save
