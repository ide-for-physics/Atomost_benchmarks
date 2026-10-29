#!/usr/bin/env python3
"""atomost-bench v1, task items (DESIGN.md): the same model gets a small hands-on task in a fresh copy of a small project
sample; arms change only how the project's memory reaches it.

  F  full index resident, no rule engine, no injection          (before round 2)
  L  lean index resident, no rule engine, no injection          (split arm: does the shorter index alone lose rules?)
  N  lean index + rule engine + memory injection (Haiku gate)   (round 2)

Isolation (DESIGN.md section 5): each run works in /tmp/w-<random>/<project folder name>, a fresh copy of
items/fixtures/<item>/; stand-in commands (bin/) come first on PATH; the fence hook (v1_fence.py, every arm) and Claude
Code's permissions keep the run inside its folder (no OS sandbox here: no unprivileged user namespaces); the engine is the frozen copy in engine/, pointed at the bench's own gov/ tree and its
own injection service (port 47627, own Haiku budget), never at the pilots' ledgers or the live service.

    python3 v1_bench.py service up|down|health
    python3 v1_bench.py run --arms F,L,N --models haiku,opus --reps 3 [--jobs 3] [--only C01,D02] [--results DIR]
    python3 v1_bench.py merge | freeze [--check] | audit [--results DIR]
Grading: v1_grade.py. A run that hits the subscription's session limit is not recorded (copied from v0's t1_bench.py)."""
import argparse
import json
import os
import random
import shutil
import signal
import subprocess
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

V1 = Path(__file__).resolve().parents[1] / "atomost-bench-v1"
ENGINE, GOV, FROZEN_BIN = V1 / "engine", V1 / "gov", V1 / "bin"
BIN = Path("/tmp/opt-tools/bin")   # where runs find the stand-ins: a neutral path (`which pw.x` must not name the bench)
ITEMS = Path(os.environ.get("AB_ITEMS", str(V1 / "items" / "items.json")))
FIXTURES = Path(os.environ.get("AB_FIXTURES", str(V1 / "items" / "fixtures")))
RESULTS = Path(os.environ.get("AB_RESULTS", str(V1 / "results")))
SCRATCH = Path("/tmp")          # runs: /tmp/w-<random>/<project folder name>, nothing in the path names the bench, arm or model
STATE = V1 / "state" / "run"
PORT = 47627
GATE_BUDGET = "2.00"
CLAUDE = str(Path.home() / ".local" / "bin" / "claude")
PY = "/usr/bin/python3"
FENCE = Path(__file__).resolve().parent / "v1_fence.py"
SHIM = Path(__file__).resolve().parent / "v1_hookshim.py"
ROOTS = {"memory-control": "~/4.memory_control", "cophon": "~/9.coherent_phonon", "deeph": "~/11.deeph"}
MODELS = {"haiku": "claude-haiku-5-5", "opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "fable": "claude-fable-5-1"}
ARMS = {"F": ("full", False), "L": ("lean", False), "N": ("lean", True)}
MAX_TURNS = "40"
TOOLS = "Read,Grep,Glob,Bash,Edit,Write"
LIMIT_TEXTS = ("hit your session limit", "hit your usage limit", "usage limit reached", "rate limit", "rate_limit", "overloaded",
               "you've reached your", "hit your weekly limit")
PROMPT_TAIL = "\n\n（你在一个无人值守的会话里，没人能回答问题；按这个项目的规矩把活干完，最后用一两句话说你做了什么。）"


def base_env(hooks: bool, ws: Path, project: str = "") -> dict:
    """The run's environment: none of this session's own ATOMOST_* or Claude Code session variables leak in."""
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("ATOMOST") or k.startswith("CLAUDE_CODE") or k in ("CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT"))}
    env.update(ATOMOST_GOV=str(GOV), ATOMOST_PROJECTS=str(GOV / "projects"), ATOMOST_STATE=str(STATE),
               ATOMOST_INJECT_PORT=str(PORT), BENCH_WS=str(ws), BENCH_LOG=str(ws.parent / ".logs"), BENCH_ROOT=ROOTS.get(project, ""), PATH=f"{BIN}:{env.get('PATH', '/usr/bin:/bin')}")
    if not hooks:
        env.update(ATOMOST_RULES="off", ATOMOST_INJECT="off")
    return env


def hook_cmd(script: str, project: str, extra: list) -> dict:
    # through the adapter: the frozen hook sees the run as if it worked in the project's real root (v1_hookshim.py)
    return {"type": "command", "command": " ".join([PY, str(SHIM), str(ENGINE / "hooks" / script), "--project", project] + extra),
            "timeout": 10 if script == "rules_hook.py" else 5}


def settings_for(arm: str, project: str, mem: Path) -> dict:
    """What `atomost` would hand a session of this project (atomost.py add_rules_hooks / add_inject_hooks), pointed at
    the frozen engine; plus the sandbox and permissions of the bench."""
    fence = {"type": "command", "command": f"{PY} {FENCE}", "timeout": 10}
    s = {"autoMemoryDirectory": str(mem),
         "permissions": {"defaultMode": "acceptEdits", "allow": ["Bash", "Read", "Grep", "Glob"]},
         "hooks": {"PreToolUse": [{"hooks": [fence]}]}}
    if ARMS[arm][1]:
        pid = f"bench-{project}"
        rh = hook_cmd("rules_hook.py", pid, ["--role", "session", "--mode", "on"])
        ih = hook_cmd("inject_hook.py", pid, ["--mode", "on"])
        s["hooks"].update({"PreToolUse": [{"hooks": [fence]}, {"hooks": [rh]}], "PostToolUse": [{"hooks": [rh]}],
                           "UserPromptSubmit": [{"hooks": [rh]}, {"hooks": [ih]}], "PostToolBatch": [{"hooks": [ih]}]})
    return s


# ---------------------------------------------------------------- the bench's own injection service
def svc_health() -> dict | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2) as r:
            return json.loads(r.read() or b"{}")
    except Exception:
        return None


def cmd_service(a) -> int:
    pidf = V1 / "state" / "service.pid"
    if a.what == "health":
        print(json.dumps(svc_health(), ensure_ascii=False))
        return 0
    if a.what == "down":
        try:
            os.kill(int(pidf.read_text()), signal.SIGTERM)
            pidf.unlink()
            print("bench service stopped")
        except Exception as e:
            print(f"not running ({e})")
        return 0
    if svc_health():
        print("bench service already up")
        return 0
    STATE.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("ATOMOST")}
    env.update(ATOMOST_GOV=str(GOV), ATOMOST_PROJECTS=str(GOV / "projects"), ATOMOST_STATE=str(STATE),
               ATOMOST_INJECT_GATE_BUDGET=GATE_BUDGET, ATOMOST_CLAUDE_BIN=CLAUDE)
    log = open(V1 / "state" / "service.log", "a")
    p = subprocess.Popen([PY, str(ENGINE / "inject_service.py"), "--port", str(PORT)], env=env, stdout=log, stderr=log,
                         start_new_session=True)
    pidf.write_text(str(p.pid))
    for _ in range(20):
        time.sleep(0.25)
        if svc_health():
            print(f"bench service up on {PORT} (pid {p.pid}, gate budget ${GATE_BUDGET}/day)")
            return 0
    print("bench service did not answer")
    return 1


# ---------------------------------------------------------------- one run
def parse_stream(lines: list) -> dict:
    out = {"final": "", "result": {}, "session": "", "ctx0": None, "calls": [], "hook_context": []}
    for ln in lines:
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            out["session"] = ev.get("session_id") or out["session"]
        if ev.get("type") == "result":
            out["result"] = ev
            out["final"] = ev.get("result") or out["final"]
        msg = ev.get("message")
        if not isinstance(msg, dict):
            continue
        u = msg.get("usage")
        if ev.get("type") == "assistant" and isinstance(u, dict) and out["ctx0"] is None:
            out["ctx0"] = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
        for b in msg.get("content") if isinstance(msg.get("content"), list) else []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                out["calls"].append({"id": b.get("id"), "tool": b.get("name"), "input": b.get("input") or {}})
            if isinstance(b, dict) and b.get("type") == "tool_result":
                for c in out["calls"]:
                    if c["id"] == b.get("tool_use_id"):
                        c["error"] = bool(b.get("is_error"))
                        c["result"] = str(b.get("content"))[:1500]
    return out


def ledger_rows(project: str, session: str) -> dict:
    out = {}
    for name in ("rules-log.jsonl", "inject-log.jsonl"):
        rows = []
        p = GOV / "projects" / f"bench-{project}" / name
        if p.is_file():
            for ln in p.read_text(errors="replace").splitlines():
                if session and f'"{session}"' in ln:
                    try:
                        rows.append(json.loads(ln))
                    except json.JSONDecodeError:
                        pass
        out[name.split(".")[0]] = rows
    return out


def snapshot_ws(ws: Path, dst: Path) -> None:
    """The run's folder after the run (small text files only), for the file checks of the grader; .manifest.json lists
    every file with its size, so a big file that was not copied still counts as present."""
    manifest = {}
    for f in ws.rglob("*"):
        rel = f.relative_to(ws)
        if f.is_symlink() or not f.is_file() or any(x == ".git" or x.endswith(".git") for x in rel.parts[:-1]):
            continue
        manifest[str(rel)] = f.stat().st_size
        if f.stat().st_size > 400_000:
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst / rel)
    dst.mkdir(parents=True, exist_ok=True)
    (dst / ".manifest.json").write_text(json.dumps(manifest, indent=0))


def git_facts(ws: Path) -> dict:
    """Commits, pushes and the index of every git repository in the run folder (the grader reads these)."""
    out = {}
    for g in [p.parent for p in ws.rglob(".git") if p.is_dir()]:
        rel = str(g.relative_to(ws)) or "."
        def run(*args):
            try:
                return subprocess.run(["git", "-C", str(g), *args], capture_output=True, text=True, timeout=20).stdout
            except Exception:
                return ""
        out[rel] = {"log": run("log", "--all", "--name-only", "--format=@@%H %s"), "status": run("status", "--porcelain"),
                    "remotes": run("remote", "-v")}
    for b in ws.rglob("*.git"):
        if b.name != ".git" and b.is_dir() and (b / "HEAD").is_file() and not (b / ".git").exists():
            try:
                out["bare:" + str(b.relative_to(ws))] = {"log": subprocess.run(["git", "-C", str(b), "log", "--all", "--format=@@%H %s"],
                                                         capture_output=True, text=True, timeout=20).stdout}
            except Exception:
                pass
    return out


def run_one(item: dict, arm: str, model: str, rep: int, out: Path, timeout: int) -> dict:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix="w-", dir=SCRATCH))
    ws, mem = run_dir / Path(ROOTS[item["project"]]).name, run_dir / "memory"
    shutil.copytree(FIXTURES / item["id"] / "ws", ws, symlinks=True)
    shutil.copytree(V1 / "arms" / item["project"] / ARMS[arm][0], mem)
    (run_dir / ".logs").mkdir()
    if (FIXTURES / item["id"] / "canned").is_dir():
        shutil.copytree(FIXTURES / item["id"] / "canned", run_dir / ".logs" / "canned")
    env = base_env(ARMS[arm][1], ws, item["project"])
    setup = FIXTURES / item["id"] / "setup.sh"
    if setup.is_file():
        subprocess.run(["bash", str(setup)], cwd=ws, env=env, capture_output=True, timeout=60)
    cmd = [CLAUDE, "-p", "--model", MODELS[model], "--output-format", "stream-json", "--verbose", "--no-session-persistence",
           "--setting-sources", "project,local", "--strict-mcp-config", "--max-turns", MAX_TURNS, "--tools", TOOLS,
           "--settings", json.dumps(settings_for(arm, item["project"], mem))]
    prompt = item["prompt"] + PROMPT_TAIL
    t0 = time.time()
    rec = {"item": item["id"], "arm": arm, "model": model, "rep": rep, "run_dir": str(run_dir)}
    try:
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ws, env=env, timeout=timeout)
        lines = p.stdout.splitlines()
        s = parse_stream(lines)
        r, u = s["result"], s["result"].get("usage") or {}
        rec.update(session=s["session"], final=(s["final"] or "")[-3000:], calls=s["calls"],
                   usage={"usd": r.get("total_cost_usd"), "seconds": round(time.time() - t0, 1), "turns": r.get("num_turns"),
                          "stop": r.get("subtype"), "ctx0": s["ctx0"], "input": u.get("input_tokens"),
                          "cache_read": u.get("cache_read_input_tokens"), "cache_write": u.get("cache_creation_input_tokens"),
                          "output": u.get("output_tokens"), "model_usage": r.get("modelUsage"),
                          "stderr": p.stderr[-600:] if p.returncode else ""})
    except subprocess.TimeoutExpired:
        lines = []
        rec.update(session="", final="", calls=[], usage={"error": f"timeout {timeout}s", "seconds": timeout})
    final = rec.get("final") or ""
    if any(t in final.lower() for t in LIMIT_TEXTS) and len(final) < 600:
        rec["usage"]["error"] = "session limit"
        shutil.rmtree(run_dir, ignore_errors=True)
        return rec
    time.sleep(1.5 if ARMS[arm][1] else 0)          # let the service write the last moment's ledger line
    rec["ledgers"] = ledger_rows(item["project"], rec.get("session", ""))
    logs = run_dir / ".logs"
    rec["stub_calls"], rec["fence"] = ([json.loads(x) for x in (logs / n).read_text(errors="replace").splitlines() if x.strip()]
                                       if (logs / n).is_file() else [] for n in ("stub.log", "fence.log"))
    rec["git"] = git_facts(ws)
    out.mkdir(parents=True, exist_ok=True)
    snapshot_ws(ws, out / "ws_after")
    (out / "run.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    (out / "transcript.jsonl").write_text("\n".join(lines) + "\n")
    shutil.rmtree(run_dir, ignore_errors=True)
    return rec


def run_paced(item, arm, model, rep, out, a, stop_file) -> dict:
    rec = {"usage": {"error": "not run"}}
    for _ in range(a.limit_retries + 1):
        if stop_file.is_file():
            return {"usage": {"error": "stopped"}}
        rec = run_one(item, arm, model, rep, out, a.timeout)
        if rec["usage"].get("error") != "session limit":
            return rec
        print(f"SESSION LIMIT {arm} {model} {item['id']}: waiting {a.limit_wait} min", flush=True)
        waited = 0.0
        while waited < a.limit_wait * 60 and not stop_file.is_file():
            time.sleep(30)
            waited += 30
    return rec


def load_items() -> list:
    return json.loads(ITEMS.read_text())


def install_standins() -> None:
    """Copy the frozen stand-ins (bin/) to the neutral path, comment lines out, the same commands; the shared script
    `_stub` becomes `.exec` (a name that does not say what it is)."""
    if BIN.exists():
        shutil.rmtree(BIN)
    BIN.mkdir(parents=True)
    for f in FROZEN_BIN.iterdir():
        name = ".exec" if f.name == "_stub" else f.name
        if f.is_symlink():
            os.symlink(".exec" if os.readlink(f) == "_stub" else os.readlink(f), BIN / name)
        else:
            lines = f.read_text().splitlines()
            body = [lines[0]] + [ln for ln in lines[1:] if not ln.lstrip().startswith("#")]
            (BIN / name).write_text("\n".join(body) + "\n")
            (BIN / name).chmod(0o755)


def cmd_run(a) -> int:
    items = load_items()
    install_standins()
    if a.only:
        want = set(a.only.split(","))
        items = [i for i in items if i["id"] in want]
    if any(ARMS[x][1] for x in a.arms.split(",")) and not svc_health():
        print("arm N needs the bench service: python3 v1_bench.py service up")
        return 2
    root = Path(a.results)
    stop_file = root / "STOP"
    tasks = []
    rng = random.Random(20261026)
    for rep in range(1, a.reps + 1):                 # rep-major: a stop part-way leaves whole reps
        block = []
        for model in a.models.split(","):
            for arm in a.arms.split(","):
                for it in items:
                    out = root / arm / model / f"rep{rep}" / it["id"]
                    if not (out / "run.json").is_file():
                        block.append((it, arm, model, rep, out))
        rng.shuffle(block)                           # arms interleaved inside a rep: no arm always meets a warm cache
        tasks += block
    print(f"{len(tasks)} runs to do", flush=True)
    root.mkdir(parents=True, exist_ok=True)
    with (root / "real_service.jsonl").open("a") as fh:     # the live service's gate spend, before (and after) each run batch
        fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "when": "start", **real_service()}) + "\n")
    usd, done = 0.0, 0
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(run_paced, it, arm, m, rep, out, a, stop_file): (it["id"], arm, m, rep) for it, arm, m, rep, out in tasks}
        for f in as_completed(futs):
            iid, arm, m, rep = futs[f]
            try:
                u = f.result().get("usage", {})
            except Exception as e:
                u = {"error": f"runner: {e}"}
            usd += u.get("usd") or 0
            done += 1
            print(f"[{done}/{len(tasks)}] {arm} {m} rep{rep} {iid}: ${u.get('usd') or 0:.3f} {u.get('turns')} turns "
                  f"ctx0 {u.get('ctx0')} {u.get('seconds')}s {u.get('error', '')} (total ${usd:.2f})", flush=True)
    with (root / "real_service.jsonl").open("a") as fh:
        fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "when": "end", **real_service()}) + "\n")
    return 0


# ---------------------------------------------------------------- merge, freeze, audit
FREEZE_FILE = V1 / "FREEZE.sha256"
REAL = Path("~/4.memory_control/projects")


def cmd_merge(a) -> int:
    items = []
    for p in ("memory-control", "cophon", "deeph"):
        f = V1 / "items" / "drafts" / f"{p}.json"
        items += json.loads(f.read_text()) if f.is_file() else []
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    ITEMS.write_text(json.dumps(items, indent=1, ensure_ascii=False))
    print(f"{len(items)} items -> {ITEMS}")
    return 0


def frozen_files() -> list:
    here = Path(__file__).resolve().parent
    fs = [V1 / "DESIGN.md", V1 / "FREEZE_NOTE.md", ITEMS, V1 / "items" / "AUTHORING.md"] + [
        here / n for n in ("v1_bench.py", "v1_grade.py", "v1_fence.py", "v1_build.py", "v1_hookshim.py")]
    for d in ("items/fixtures", "arms", "gov", "engine", "bin"):
        fs += [f for f in (V1 / d).rglob("*") if f.is_file() and "__pycache__" not in f.parts
               and not (d == "gov" and f.name.endswith("-log.jsonl"))]
    return sorted(set(fs))


def sha(f: Path) -> str:
    import hashlib
    return hashlib.sha256(f.read_bytes()).hexdigest()


def cmd_freeze(a) -> int:
    if a.check:
        want = dict(reversed(ln.split("  ", 1)) for ln in FREEZE_FILE.read_text().splitlines() if ln.strip())
        now = {str(f): sha(f) for f in frozen_files()}
        changed = [f for f in want if now.get(f) != want[f]]
        added = [f for f in now if f not in want]
        print(f"{len(want)} frozen files: {len(changed)} changed or missing, {len(added)} new")
        for f in changed + added:
            print("  ", f)
        return 1 if changed or added else 0
    if FREEZE_FILE.exists() and not a.force:
        print("already frozen; --force to re-freeze (only before any real run)")
        return 2
    lines = [f"{sha(f)}  {f}" for f in frozen_files()]
    FREEZE_FILE.write_text("\n".join(lines) + "\n")
    print(f"froze {len(lines)} files -> {FREEZE_FILE}")
    return 0


def real_service() -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:47617/health", timeout=2) as r:
            d = json.loads(r.read() or b"{}")
        return {k: d.get(k) for k in ("gate_day", "gate_calls", "gate_cost", "gate_dropped", "events", "started")}
    except Exception as e:
        return {"error": str(e)}


def cmd_audit(a) -> int:
    root = Path(a.results)
    runs = [json.loads(p.read_text()) for p in sorted(root.glob("*/*/rep*/*/run.json"))]
    sids = {r.get("session") for r in runs if r.get("session")}
    run_dirs = {r.get("run_dir") for r in runs if r.get("run_dir")}
    leaks = []
    for p in sorted(REAL.glob("*/*-log.jsonl")):
        with p.open(errors="replace") as fh:
            for n, ln in enumerate(fh, 1):
                if any(s in ln for s in sids) or any(d in ln for d in run_dirs):
                    leaks.append(f"{p}:{n}")
    bench_dirs = [str(p) for p in REAL.glob("bench-*")]
    fence = [(r["item"], r["arm"], r["model"], r["rep"], f.get("why", "")[:120]) for r in runs for f in r.get("fence") or []]
    home_reads = sorted({f"{c['tool']}:{c['input'].get('file_path') or c['input'].get('path') or ''}" for r in runs for c in r.get("calls") or []
                         if not c.get("error") and str(c["input"].get("file_path") or c["input"].get("path") or "").startswith("/home/")})
    rep = {"runs": len(runs), "sessions": len(sids), "real_ledger_lines_with_bench_sessions": leaks, "real_bench_dirs": bench_dirs,
           "fence_refusals": len(fence), "fence_by_reason": {}, "home_paths_read_ok": home_reads, "real_service_now": real_service()}
    for _, _, _, _, why in fence:
        k = why.split("(")[0].split(";")[0][:60]
        rep["fence_by_reason"][k] = rep["fence_by_reason"].get(k, 0) + 1
    (root / "AUDIT.json").write_text(json.dumps({**rep, "fence": fence}, indent=1, ensure_ascii=False))
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 1 if leaks or bench_dirs else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("service")
    s.add_argument("what", choices=["up", "down", "health"])
    r = sub.add_parser("run")
    r.add_argument("--arms", default="F,L,N")
    r.add_argument("--models", default="haiku")
    r.add_argument("--reps", type=int, default=1)
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--only", default="")
    r.add_argument("--results", default=str(RESULTS))
    r.add_argument("--timeout", type=int, default=900)
    r.add_argument("--limit-retries", type=int, default=6)
    r.add_argument("--limit-wait", type=float, default=30)
    sub.add_parser("merge")
    fz = sub.add_parser("freeze")
    fz.add_argument("--check", action="store_true")
    fz.add_argument("--force", action="store_true")
    au = sub.add_parser("audit")
    au.add_argument("--results", default=str(RESULTS))
    a = ap.parse_args()
    return {"service": cmd_service, "run": cmd_run, "merge": cmd_merge, "freeze": cmd_freeze, "audit": cmd_audit}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
