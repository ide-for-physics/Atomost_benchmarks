#!/usr/bin/env python3
"""Sum node-hours from jobs.log lines of the form '... = X NH ...'."""
import re, sys
fn = sys.argv[1] if len(sys.argv) > 1 else 'jobs.log'
tot = 0.0; n = 0
for line in open(fn):
    if line.startswith('#'): continue
    m = re.search(r'=\s*([\d.]+)\s*NH', line)
    if m:
        tot += float(m.group(1)); n += 1
print(f"{n} finished jobs, total {tot:.3f} node-hours (budget 20)")
