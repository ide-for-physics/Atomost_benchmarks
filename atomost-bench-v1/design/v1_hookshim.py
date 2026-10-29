#!/usr/bin/env python3
"""atomost-bench v1 hook adapter (arm N only): shows the frozen atomost hooks the run as if it worked in the project's real
root. The rules are anchored to real roots (`cwd: ^~/11\\.deeph`, `path: ^~/4\\.memory_control/_archive`),
and a run works in /tmp/w-<random>/<project folder name>, so without this they never fire. Editing the frozen rule copies
instead would change the data under test and void the owner's approvals (bound to each rule's `when` + `do`).

It replaces $BENCH_WS with $BENCH_ROOT in the hook's input (cwd, tool input, transcript text), runs the frozen hook with
the same arguments, and passes its answer through unchanged. The fence (v1_fence.py) still sees the true paths.
    v1_hookshim.py <frozen hook script> [its arguments...]"""
import os
import subprocess
import sys


def main() -> int:
    raw = sys.stdin.buffer.read()
    ws, root = os.environ.get("BENCH_WS", ""), os.environ.get("BENCH_ROOT", "")
    if ws and root:
        raw = raw.replace(ws.encode(), root.encode())
    try:
        p = subprocess.run([sys.executable] + sys.argv[1:], input=raw, capture_output=True, timeout=9)
    except Exception:
        return 0                                   # fail open, like the hooks it wraps
    sys.stdout.buffer.write(p.stdout)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
