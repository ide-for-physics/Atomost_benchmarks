#!/bin/bash
# Usage: make_fine_run.sh NKF NWF NSKIP EF OMIN OMAX OSTEP NODES TIME  -> writes inputs/fine_NKF/epw_fine.in and job script
set -e
NKF=$1; NWF=$2; NSKIP=$3; EF=$4; OMIN=$5; OMAX=$6; OSTEP=$7; NODES=$8; TIME=$9
D=<whiteboard>/NbFeSb_whiteboard
OUT=$D/inputs/fine_k${NKF}
mkdir -p $OUT
sed -e "s/__NWF__/$NWF/" -e "s/__NSKIP__/$NSKIP/" -e "s/__EF__/$EF/" -e "s/__OMIN__/$OMIN/" -e "s/__OMAX__/$OMAX/" \
    -e "s/__OSTEP__/$OSTEP/" -e "s/__NKF__/$NKF/g" $D/inputs/epw_fine.in.template > $OUT/epw_fine.in
sed -e "s/__NAME__/epwk${NKF}/" -e "s/__NODES__/$NODES/" -e "s/__TIME__/$TIME/" -e "s#__DIR__#fine_k${NKF}#" \
    -e "s/__INPUT__/epw_fine.in/" -e "s/__OUTPUT__/epw_fine.out/" $D/inputs/job_epw_template.sh > $OUT/job_epw_fine.sh
echo "wrote $OUT"
