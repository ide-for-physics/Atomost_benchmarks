# atomost-bench v2 — 冻结说明

冻结的内容见 `FREEZE.sha256`（`python3 ../atomost_bench/v2_bench.py freeze` 生成，`freeze --check` 复核）。

## 取自哪里

- 2026-10-27 14:2x 由 `v2_build.py` 取 atomost 当时的状态：提交 4f7ffbb（被测代码和规则与 d28a782 相同，之后只多了一行日志）。
  工作区里没提交的改动（规则、记忆、引擎目录下 112 个文件，多是 strategist 的整理）按原样取；这些改动连同未跟踪文件的
  diff 哈希前 16 位：1bb6124e67f91bbd。
- 规则页上没有等着的提议（三条"拦一次"owner 14:06–14:08 已批）；冻结的规则副本里全机 16 条、memory-control 19 条、cophon 25 条、
  deeph 28 条，全部是"生效"状态。
- 两个 strategist 收窄触发字段的结论已落进记忆文件（cophon：kernel-pipeline-review-baseline、kernel-numerics；deeph：
  local-parallel-limit-blas-threads、explorer-site-shared），快照里就是收窄后的样子。
- 索引大小和 v1 一字不差：memory-control 全量 / 精简 655 / 476，cophon 2,555 / 1,126，deeph 2,147 / 1,127 token。

## 和 v1 一样的

- 题目、答案键、小项目样本、假命令：从 v1 原样复制，逐个文件哈希与 v1 相同。
- 判分器、围栏、适配层、跑法：v1 脚本复制成 v2_*，只改目录名。跑法另记每次的开始时间（附带指标用）。

## 新加的

- `v2_compare.py`：逐条对 v1（DESIGN 第 4 节）、误推前后对比、附带指标"追加进日志的行时间对不对"。附带指标对 v1 的结果
  先算过一次：F 组 63 行里 6 行时间不对，N 组 70 行里 1 行。

## 冻结前对冻结引擎的机械核对（零模型花费）

v1 漏掉的几种写法现在都响：`cd x && OMP_NUM_THREADS=1 mpirun …`、`export OMP_NUM_THREADS=1; mpirun …` → heavy 规则；
多行 `for …; do⏎ ssh … &⏎ done` → 并发 ssh 规则（拦下）；`sed … > <某个运行目录>/epw.in` → epw-input-by-shell（提醒）；
`ssh nic6 …` → 先读手册（拦一次）；`echo '2026-10-27 09:00 · …' >> RUNNING.log` → 日志不带日期（拦一次）。

## 已知、没改的

- D04 假 pw.x 输出与输入对不上（v1 报告已写）；两组相同。
- epw-input-by-shell 是提醒级：sed 写完才到，会话要自己回头改；判分看最终文件。
