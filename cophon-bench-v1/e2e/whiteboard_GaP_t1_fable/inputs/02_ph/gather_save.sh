#!/bin/bash
# Equivalent of EPW/bin/pp.py (non-interactive): collect dyn files, dvscf and patterns into save/
cd "$(dirname "$0")"
PREFIX=gap; OUT=../01_scf/tmp_ph
NQ=$(awk 'f{print $1; exit} /NUMBER_OF_Q_POINTS/{f=1}' $OUT/_ph0/$PREFIX.phsave/control_ph.xml)
echo "nq irreducible = $NQ"
mkdir -p save
for i in $(seq 1 $NQ); do
  cp $PREFIX.dyn$i save/$PREFIX.dyn_q$i
  if [ $i -eq 1 ]; then
    cp $OUT/_ph0/$PREFIX.dvscf1 save/$PREFIX.dvscf_q1 2>/dev/null || cp $OUT/_ph0/$PREFIX.dvscf save/$PREFIX.dvscf_q1
    cp -r $OUT/_ph0/$PREFIX.phsave save/
  else
    cp $OUT/_ph0/$PREFIX.q_$i/$PREFIX.dvscf1 save/$PREFIX.dvscf_q$i 2>/dev/null || cp $OUT/_ph0/$PREFIX.q_$i/$PREFIX.dvscf save/$PREFIX.dvscf_q$i
  fi
done
ls -la save | head -40
