#!/usr/bin/env python3
"""atomost-bench v1 fence (DESIGN.md section 5): a PreToolUse hook in every arm, the same in all three. This machine has no
unprivileged user namespaces (bwrap fails), so Claude Code's own sandbox cannot run; the fence and Claude Code's
permission system keep a run inside its own folder instead.

Refuses: any tool call naming a path under the home folder or ~ / $HOME outside the read-only list below; a writing
command or a file edit that names any home path; an edit or write outside the run folder; a script written with a home
path in it. Every refusal goes to $BENCH_LOG/fence.log (the isolation audit reads it). Fails CLOSED: an error of its
own refuses the call - the opposite of the atomost hooks, because here the risk is a real project, not a lost session.
Logs go to $BENCH_LOG (the run folder's .logs/, beside the work folder, so a `git add -A` in the task never sweeps them up)."""
import json
import os
import re
import sys
import time

HOME = os.path.expanduser("~")
V1 = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "atomost-bench-v1"))
READ_OK = [os.path.join(V1, "arms"), "~/4.memory_control/handbooks",
           os.path.join(HOME, ".claude", "CLAUDE.md")]
PATH_RE = re.compile(r"(?:(?<![\w~])~(?=/)|\$HOME\b|\$\{HOME\}|" + re.escape(HOME) + r"(?=/|\s|$|['\"]))[^\s'\"|;&><)`]*")
WRITE_RE = re.compile(r">|\btee\b|\bsed\s+-i|\bperl\s+-i|(^|[;&|\s(])(cp|mv|rm|rmdir|touch|mkdir|ln|chmod|chown|install|truncate|dd|"
                      r"rsync|git|python3?|bash|sh|zsh|perl|node|make|unzip|tar|kill|pkill|systemctl|crontab)(\s|$)")


NET_KILL_RE = re.compile(r"(^|[;&|\s(`])(curl|wget|nc|ncat|telnet|ftp|kill|/usr/bin/\w+/?(ssh|scp|rsync|sftp|pkill|killall)|/usr/bin/(ssh|scp|rsync|sftp|pkill|killall))(\s|$)")


BARE_HOME_RE = re.compile(r"(^|[;&|\s(])(cd|pushd|ls|du|find|grep|rg|cat)\s+(-\S+\s+)*(~|\$HOME|\$\{HOME\})(\s|$|[;&|)])")
TOOLS_DIR = "/tmp/opt-tools"           # the stand-ins: may be run, not read
READ_VERB_RE = re.compile(r"(^|[;&|\s(`])(cat|head|tail|less|more|file|strings|od|xxd|hexdump|sed|grep|rg|awk|cp|bat|nl|vi|vim|nano|diff)\s[^;&|\n]*" + re.escape(TOOLS_DIR))


def norm(p: str) -> str:
    p = re.sub(r"^(~|\$HOME|\$\{HOME\})", HOME, p)
    return os.path.normpath(p)


def outside_read_ok(paths: list) -> list:
    return [p for p in paths if not any(norm(p) == r or norm(p).startswith(r + "/") for r in READ_OK)]


def decide(d: dict, ws: str) -> str:
    tool, inp = d.get("tool_name") or "", d.get("tool_input") or {}
    run = os.path.dirname(ws)
    if ".logs" in json.dumps(inp) and (run + "/.logs" in json.dumps(inp) or re.search(r"(^|[\s/'\"])\.\./\.logs|\.logs/(canned|stub|fence)", json.dumps(inp))):
        return f"sandbox: this run may only work in its own folder ({ws})"
    if tool == "Bash":
        cmd = str(inp.get("command") or "")
        if BARE_HOME_RE.search(cmd):
            return f"sandbox: this run may only work in its own folder ({ws}); refused path ~"
        if READ_VERB_RE.search(cmd):
            return f"sandbox: {TOOLS_DIR} holds system tools; run them, do not read or copy them"
        if NET_KILL_RE.search(cmd):
            return "sandbox: no network commands, no kill, no real ssh/rsync in this run"
        homes = PATH_RE.findall(cmd)
        plain = re.sub(r"\d?>&\d|\d?>>?\s*/dev/null", " ", cmd)      # 2>&1, >/dev/null: not writes
        bad = outside_read_ok(homes)
        if bad:
            return f"sandbox: this run may only work in its own folder ({ws}); refused path {bad[0]}"
        if homes and WRITE_RE.search(plain):
            return f"sandbox: no writing command may name a path outside this run's folder ({ws}); refused {homes[0]}"
        return ""
    if tool in ("Read", "Grep", "Glob", "NotebookRead"):
        p = str(inp.get("file_path") or inp.get("path") or "")
        if p.startswith(TOOLS_DIR):
            return f"sandbox: {TOOLS_DIR} holds system tools; run them, do not read or copy them"
        cand = [p] if p.startswith("/") or p.startswith("~") else []
        if cand and not os.path.normpath(norm(p)).startswith(run) and outside_read_ok(cand):
            return f"sandbox: this run may only read its own folder ({ws}) and the handbooks; refused {p}"
        return ""
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        p = norm(str(inp.get("file_path") or inp.get("notebook_path") or ""))
        if not p.startswith("/"):
            p = os.path.normpath(os.path.join(d.get("cwd") or ws, p))
        if not (p.startswith(ws + "/") or p.startswith(os.path.join(run, "memory") + "/")):
            return f"sandbox: edits only inside this run's folder ({ws}); refused {p}"
        if re.search(r"\.(py|sh|bash|pl|js)$", p) and outside_read_ok(PATH_RE.findall(str(inp.get("content") or inp.get("new_string") or ""))):
            return "sandbox: a script written here may not name paths outside this run's folder"
        return ""
    return ""


def main() -> None:
    ws = os.environ.get("BENCH_WS", "")
    try:
        d = json.load(sys.stdin)
        why = decide(d, ws) if ws else "sandbox: BENCH_WS not set"
    except Exception as e:
        d, why = {}, f"sandbox: error {e}"
    if not why:
        return
    try:
        logd = os.environ.get("BENCH_LOG") or os.path.join(os.path.dirname(ws), ".logs")
        os.makedirs(logd, exist_ok=True)
        with open(os.path.join(logd, "fence.log"), "a") as fh:
            fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": d.get("tool_name"),
                                 "input": json.dumps(d.get("tool_input") or {}, ensure_ascii=False)[:600], "why": why},
                                ensure_ascii=False) + "\n")
    except Exception:
        pass
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": why}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
