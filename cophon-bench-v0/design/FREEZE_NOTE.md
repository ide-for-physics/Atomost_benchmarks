# 冻结清单说明（2026-10-14 23:15）

`FREEZE.sha256`（白板跑之前封的，67 个文件）23:10 复核：标签（labels/ 19 个）、A 的 44 张工单（kernel_pipeline/bench/tickets 19 张 + benchmarks/cophon_bench/tickets_ext 25 张）、pillar_b.py、pillars_cd.py 全部未变（46 + 19 = 65 个 OK）。

两个脚本在冻结后改过，如实记：
- `benchmarks/cophon_bench/pillar_a.py`：`_tolerant()`（把被截断的 JSON 答案尽量解析成对象）原来在找不到右括号时直接放弃，改成先补括号再试；判分规则（类别分、最佳动作、烧算力）没有动。影响：14 份被截断的白板 Fable 答案从"解析不出"变成可判。
- `benchmarks/cophon_bench/run_models.py`：`--max-turns` 改为从环境变量取（默认 6，重答时 15），并加了"回复是订阅额度用尽的提示文本就不落盘"的保护。影响：Fable/Opus 的 91 份空答得以重答，不被当成"非法"判分。

两处都是修"答案进不了判分器"的问题，不是改判分标准；改动当时记在 RUNNING.log 19:10 条。新清单 `FREEZE_v0.1.sha256`（路径全部相对项目根目录）含上述脚本的当前哈希，另加 a_best.py、b_round2.py、b_drive.py、ticket_relay.py、logs/wb_audit.py。

## 关键点搬家（2026-10-15）

基准目录从 `records/2026-10-14/cophon-bench-v0/` 搬到 `benchmarks/cophon-bench-v0/`，端到端材料库从 `benchmarks/cophon_bench/e2e_library/` 搬到
`benchmarks/cophon-bench-v0/e2e_library/`。`FREEZE_v0.1.sha256` 的 72 个文件在新路径下逐个复核，内容全部未变（sha256 全对）；
新清单 `FREEZE_checkpoint_2026-10-15.sha256` 是同一批文件按新路径重列。`b_runtime/common.py` 与 `prep_inputs.py` 里的记录路径常量随之改为新路径
（两者不在冻结清单里，不参与判分）。
