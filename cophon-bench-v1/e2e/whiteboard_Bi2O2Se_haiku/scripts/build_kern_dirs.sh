#!/bin/bash
# Build self-contained EPW reuse directories (epwread/epbread) for a given fine mesh N.
# Usage: build_kern_dirs.sh N   (run on LUMI from $ROOT)
set -e
N=$1
D=kern$N
rm -rf $D; mkdir -p $D/tmp/bi2o2se.save
cp run/tmp/bi2o2se.save/data-file-schema.xml run/tmp/bi2o2se.save/charge-density.dat $D/tmp/bi2o2se.save/
for f in run/tmp/bi2o2se.epb*; do ln -s "../../$f" "$D/tmp/$(basename $f)"; done
cp -r run/save $D/save
cp run/epwdata.fmt run/bi2o2se_wsvec.dat run/bi2o2se_hr.dat run/bi2o2se.kgmap run/bi2o2se.kmap $D/
cp run/bi2o2se.win $D/ 2>/dev/null || true
echo "built $D"
