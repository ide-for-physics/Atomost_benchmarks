#!/usr/bin/env python3
import re, sys
txt = open(sys.argv[1]).read()
st = {int(n): (el, int(l)) for n, el, l in re.findall(r"state #\s*(\d+): atom\s+\d+ \((\w+)\s*\), wfc\s+\d+ \(l=(\d+) m=", txt)}
lab = {0: 's', 1: 'p', 2: 'd'}
kblocks = txt.split(" k = ")[1:]
for ik in [0, 40, 80, 120]:
    kb = kblocks[ik]
    print("k =", kb[:40].split("\n")[0])
    for m in re.finditer(r"==== e\(\s*(\d+)\) =\s*([-\d.]+) eV ====\s*\n(.*?)\|psi\|\^2 = ([\d.]+)", kb, re.S):
        ib = int(m.group(1)); e = float(m.group(2)); body = m.group(3)
        if ib < 20 or ib > 34:
            continue
        comp = {}
        for w, n in re.findall(r"([\d.]+)\*\[#\s*(\d+)\]", body):
            el, l = st[int(n)]
            key = el + '-' + lab[l]
            comp[key] = comp.get(key, 0) + float(w)
        top = sorted(comp.items(), key=lambda x: -x[1])[:4]
        print("  band %2d %7.3f eV: " % (ib, e) + "  ".join("%s %.2f" % kv for kv in top) + "  |psi|^2=" + m.group(4))
