#!/bin/bash
# usage: summarize_wan_tests.sh  (run from the local project root after fetching wan_*/ results into results/wannier_tests/)
cd <whiteboard>/GaP_whiteboard
for d in results/wannier_tests/wan_*; do
  n=$(basename $d)
  echo "=================== $n"
  grep -A1 "Final Spread" $d/gap.wout | head -2 | tr -s ' '
  grep -E "Disentanglement convergence criteria satisfied|Wannierisation convergence criteria satisfied|exceeded|not converged" $d/gap.wout | head -3
  awk '/Final State/{f=1} f&&/WF centre and spread/{print $NF}' $d/gap.wout | sort -g | awk '{a[NR]=$1} END{printf "spreads: min %.2f max %.2f (n=%d)\n", a[1], a[NR], NR}'
  grep "WANNIER  *:" $d/epw_wan_*.out | tail -1
  python3 -I scripts/parse_w90bands.py results/04_bands/bands.out $d/gap_band.dat 7.6046 9.2019 5 "$n" | grep -v "^check"
done
