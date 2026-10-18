# cophon-bench v1 · 冻结说明（2026-10-15 10:40，开跑前）

`FREEZE_v1.sha256`（112 个文件，路径相对项目根目录）在任何 v1 的模型运行、飞行或白板会话之前写下。里面有：

- **标签**：端到端基线 `labels/E_baselines.json` 与封存晶胞 `labels/cells/`（10 个候选，8 个入选）；运维题工单 44 张（`kernel_pipeline/bench/tickets/T*`
  19 张 + `cophon_bench/tickets_ext/X*` 25 张）与留出集 7 张（`cophon_bench/tickets_holdout/H*`；今天再收一次，10-15 08:00 以后真材料库里没有新工单，
  所以仍是 H01–H07）；Wannier 题的 16 份输入沿用 v0 的 `cophon-bench-v0/labels/b_inputs/`（未变）；选材/峰位的 v0 标签 `materials.json`、`candidates_C.json`
  （选材池扩完后**第二阶段**重冻结，见下）。
- **判分器与运行器**：`pillar_a/b/cd/e.py`、`run_models.py`、`ticket_relay.py`、`b_drive.py`、`b_round2.py`、`b_roundn.py`、`a_best.py`、`holdout_build.py`、
  `c_expansion_sample.py`、`b_runtime/{common,materialize,prep_inputs}.py`、流水线自己的工单提示渲染器 `kernel_pipeline/bench/bench.py`。
- **设计输入**：`design/C_expansion_sample.json`、`whiteboard/TASK_TEMPLATE.md`、`whiteboard/sandbox/Dockerfile`、基准库的配置 `e2e_library/kernel_pipeline_bench.toml`。
- **harness 版本**：`kernel_pipeline/BASELINE.sha256` = **kernel_pipeline v2.0.12**（2026-10-15 09:15 封存，规则 Q1 调度）。v1 测的是这个版本；
  v0 发现、交接给线 2 的三处不足（晶胞静默退回、打包作业每步超时、Wannier 墙钟）在这个版本里修了哪些，报告按实测写。
- **案例库快照**：基准库 `e2e_library/_library/{casebook,wannier_events.jsonl}` 是 2026-10-15 10:10 从真材料库复制的（清单
  `_library/SNAPSHOT_from_materials_2026-10-15.sha256`，17 个文件）；飞行期间不再同步。

## 与 v0 冻结相比改过的脚本（冻结前改，属于 v1 的设计）

- `run_models.py`：加节奏控制（`--pace`，每次 Claude 调用前停几秒）与额度等待（`--limit-wait/--limit-retries`，回复是订阅额度用尽的提示文本时等一段再重问，
  不落盘），`STOP` 文件可平稳停止。判分无关。
- `ticket_relay.py`：加 `--all --apply`——按材料名后缀选操作员模型（`_e2eH`/`_cx` → Haiku，`_e2eF` → Fable），校验通过且不是升级（escalate）的答案写到
  工单旁边由监督器应用；升级与连续三次无效答案留给人（`results/e/relay/ESCALATIONS.md`），每条算一次人工触碰。v1 不再跑影子模型。
- `b_runtime/common.py`、`materialize.py`：按 `COPHON_BENCH_VERSION=v1` 选版本目录与远端根（`bench_b_v1`）；打包作业里每个 srun 步骤包一层 `timeout`
  （默认为包墙钟的 60%，至少 10 分钟）——v0 两次 pw2wannier90 挂死到 6 小时墙钟、整包陪葬的问题，是基准自己运行时的事，不在 harness 交接单里。
- `b_roundn.py`：b_round2 的推广（第 N 轮带前 N−1 轮各自的尝试与分数）。
- `pillar_a.py`：`--holdout`（上一条记录已写）。`pillar_e.py`：新。其余判分器未动。

## 重复次数：主集 5 次 = v0 的 3 次 + 新跑 2 次

运维题主集 44 张的两臂提示词今天重新生成并与 v0 的 88 份逐字节比对：**全部相同**（10-15 10:20）。模型 ID 也相同（haiku 5.5 / sonnet 5.5 / opus 5.5 /
fable 5.1 / deepseek-v4-flash）。因此 v0 的 3 次回答作为 v1 主集的第 1–3 次（原样复制到 `results/a/*/rep1-3`，1320 份文件），新跑第 4–5 次；
留出集 7 张全部新跑 5 次。这样省掉约 1000 次 Claude 调用（所有者的订阅窗与我们同时在用）。

## 第二阶段冻结（计划）

选材池扩完（10 个 `_cx` 材料出核）后：重建 C/D 标签（`pillars_cd.py labels` 需要能读基准库里的核——这是下一步代码改动，改完连同新标签一起列入
`FREEZE_v1_stage2.sha256`），然后才跑选材题的模型。峰位题不再跑模型（阴性对照用 v0 结果）。

## 冻结后的任何改动

写在本文件下面，不悄悄刷新清单。

### 2026-10-15 11:45 · 端到端 harness 臂：三个材料的六条飞行重建（基准自己的配置错，不是判分改动）

- **发生了什么**：16 条 harness 臂统一用 `--relax fixed --cell-policy pbesol` 建。Bi2O2Se、MoS2 单层、SnS2 的两条臂都卡在第一步（relax 门：残余压强 −36.3、−8.2、+9.7 kbar，
  门槛 1 kbar），中继的操作员模型（Haiku 与 Fable 各自）都正确地升级给 construction。
- **原因（查实）**：(1) 基准的配置错——这三个基线的封存晶胞不是 PBEsol 弛豫出来的：Bi2O2Se 与 MoS2 单层是 PBE 变胞弛豫（基线 relax.in `input_dft='PBE'`，
  同截断下压强 0.17、0.02 kbar），SnS2 是实测晶胞（COD，a = 3.639、c = 5.868 Å）+ PBE 内坐标；在固定晶胞上换 PBEsol 必然有残余压强。
  (2) harness v2.0.12 的不足：`relax fixed` 仍按"变胞步"判门，压强照查（只有两步法的 ions 步才去掉压强一项），还会按规则 C3 把它当"第二次变胞"重提一次。
  这一条交给线 2（`records/handoffs/2026-10-15-bench-v1-harness-findings-for-line2.md`），基准不修。
- **处理**：六个第一次尝试原样归档到 `e2e_library/_attempt1/`（不删；共用了约 466 节点秒 ≈ 0.13 节点时，报告里单列）；同名重建：
  Bi2O2Se、MoS2 单层 → `--relax fixed --cell-policy pbe`（与基线同一泛函，只松弛内坐标）；SnS2 → `--relax none --cell-policy pbe`（封存的内坐标就是基线在这个晶胞上的
  PBE 弛豫结果；v2.0.12 里没有能在实测晶胞上过 relax 门的 fixed 路线）。晶胞文件不变（sha256 同前）。白板臂不受影响（任务书本来就只给封存晶胞）。
- **对结论的影响**：判分规则、标签、晶胞都没动。报告里这三个材料的 harness 臂墙钟从重建时刻算，第一次尝试的节点时与"卡住"如实单列为
  "基准配置错 + harness 不足"，不计入 harness 的人工触碰（那是我们的配置错），但 harness 不足本身写进缺口附录。

### 2026-10-15 11:45 · 运行中的 harness 版本：v2.0.12 与 v2.0.13 混跑（只差振幅报数）

- 流水线是可编辑安装，v2.0.13 在 10:57 封存（线 2，振幅约定 Q̄E0²T|Γ|/(2ħ)、M0 = 1 amu）。10:57 以前启动的驱动进程跑 v2.0.12，以后启动或重启的跑 v2.0.13；
  每条门记录都盖了实际版本章（`gate["code"]`，按进程缓存），可以逐条查。
- v2.0.13 只改报告里的位移振幅（× 1.5771）；核文件、不变量、包络、收敛与所有门槛不变（提交说明与 diff：只动 `lib/epw.py` 的 `displacement_amplitude` 和 `lib/report.py` 的说明）。
  端到端判分只用核文件的不变量谱（峰位、峰高 Å²/eV、模式频率），**不受影响**；不重跑、不钉版本。报告写"harness = v2.0.12/v2.0.13（判分相关部分相同）"。

### 2026-10-15 11:45 · 记一条与基线的路线差别（不处理）

- 过了 relax 的五个材料（GaP、CdS、KNbO3、InPS4、NbFeSb）在 `fixed + pbesol` 下用 **PBEsol** 松弛内坐标，之后各阶段用 PBE；基线是 PBEsol 定胞、**PBE** 松内坐标。
  GaP、NbFeSb 的内坐标由对称性定死，无差别；CdS（u）、KNbO3、InPS4 有自由内坐标，可能有小差别。v2.0.12 的 fixed 路线没有"PBE 松内坐标、不查压强"的组合，
  所以不重建；这三个材料若判成"不同答案"，先查这一条。

### 2026-10-15 17:05 · 运行器认不出"单个模型用量已满"的提示（冻结文件 `cophon_bench/run_models.py` 改一行；不涉及提示词、标签、判分）

- **发生了什么**：约 16:50 起 Fable 的回答变成 "You've reached your Fable limit. Switch to another model, …"（按模型计的上限，与 5 小时窗的
  "hit your session limit" 措辞不同）。运行器的额度识别表里没有这句，于是把它当成普通回答写下、记"无法解析"：A 组 harness 臂 Fable 第 5 次的
  X13–X24 共 12 题，每题约 2 s、$0。
- **处理**：12 份记录移到 `results/a/_limit_burned_2026-10-15/A_harness/fable/rep5/`（原样保留作证据），不计分，Fable 额度恢复后重做；
  `run_models.py` 的 `LIMIT_TEXTS` 加一条 "you've reached your"（测过：这句和原来的会话上限句都认作额度提示，正常的答案 JSON 不会误认）。
  中继 `ticket_relay.py` 用的是同一个识别函数，所以 Fable 臂的工单在 Fable 额度满时也改为"下一轮重试"，不会因为连续三次"无效答案"误交给人。
- **运行方式**：离线单元 16:59 停下、17:0x 重启，`offline_v1.sh` 新增 `OFFLINE_MODELS`，先只跑 Haiku、Sonnet、Opus（所有者 17:00："除了要用 fable 的，其他都执行"），
  Fable 的剩余题目等它的额度恢复后补跑（运行器可续跑，已有答案跳过）。
- 清单 `FREEZE_v1.sha256` 不刷新：`run_models.py` 的哈希从此与清单不符，原因就是本条。

### 2026-10-17 07:57 · 运行器认不出"每周额度"的提示（冻结文件 `cophon_bench/run_models.py` 改一行；不涉及提示词、标签、判分）

- **发生了什么**：白板 Fable 臂用的第二账号 06:05 前后回复 "You've hit your weekly limit · resets Oct 19, 9am (UTC)"——第三种额度措辞。
  白板侧两条臂（CdS、InPS4）因此被调度脚本当成"自己结束"；离线运行器此刻没在跑，没有记下任何此类回答（重启前改好）。
- **处理**：`run_models.py` 的 `LIMIT_TEXTS` 加一条 "hit your weekly limit"（识别函数先转小写，与另外两句同样处理；长度 < 600 的限制不变，正常答案 JSON 不会误认）。
  白板侧的 `fable_sched.sh`、`continue_next.sh` 同样加这一句（它们不在冻结清单里）。
- 清单 `FREEZE_v1.sha256` 不刷新：`run_models.py` 的哈希从此与清单不符，原因是 10-15 17:05 与本条两次。

### 2026-10-17 08:20 · 第二阶段冻结：选材题 C 的扩池标签与提示词（`FREEZE_v1_stage2.sha256`，27 个文件）

- **时机**：10 个扩池材料（基准库 `e2e_library/<M>_cx`）10-17 06:24 全部出核（最后一个 SnI4）；任何模型作答 C 第二阶段之前写下本清单。
- **真值怎么来**：新脚本 `cophon_bench/c_stage2.py`。它不改探索器的代码，原样调用探索器的出卡程序 `export_cards.py` 和筛选打分 v2.1（`export_screening.py` → `source_score_v21.py`，
  打分器自带的规则：主分中点 ≥ 0.5 × LiNbO3 才算"有希望"，与 v0 标签相同，阈值 1.511），以及冻结的 `pillars_cd.build_labels`。三者都指向临时搭的影子项目：
  影子里 `materials/` 是真材料库各目录的链接；10 个抽中的名字换成基准库 `<M>_cx` 各文件的链接，再加上 `materials/<M>/prior.json`，也就是抽样时用的先验。
  输出写到 `labels/C_stage2/explorer_data/`。真材料库、基准库、探索器都没写入：运行前后比对，只多了 `scripts/__pycache__` 两个字节码缓存文件。
- **自检**：影子里重出的标签里，v0 的 42 条记录中有 40 条卡片没变，这 40 条逐字段与 v0 冻结标签相同（真值、白板特征、harness 特征）；另 2 条 CdS_mp672、NbFeSb_mp9437 已被探索器的 _kp 版本取代，
  按 v0 冻结原样保留。
- **池子**：v0 的 37 个候选 + 新 10 个 = 47 个，化学式无重复；每批仍选 8 个，判分不变（`pillars_cd.py grade`）。新材料在提示词和标签里用原名 `<M>`，不带 `_cx`，
  与其他候选一样，也因此计入"循环发现的池子"那一子表。
- **新 10 个材料的真值**：都不是"有希望"。主分最高的是 TiPbO3 0.54，其余在 0.08 以下或为 0；只有 LiZnPS4 一个"命中激光线且辐射"；Be2C、NaPN2、AlN、AlAsO4 的核峰落在 6 eV 窗口边上。
  整池"有希望"仍是 4 个，"命中激光线且辐射"从 15 个变成 16 个（以 `labels/C_stage2/STAGE2_CHECK.md` 为准）。
  TiPbO3 的卡片带一条导出提示："核的简并与声子解不匹配"（审查项 C2，非严格模式照常出卡，见 `explorer_data/export_issues.json`）。
- **提示词**：`prompts/C2_whiteboard/C_whiteboard.prompt.txt`（1.8 万字符）、`prompts/C2_harness/C_harness.prompt.txt`（14.9 万字符），用冻结的 `pillars_cd.py prompts` 生成，
  两份提示词正文与 v0 相同，只多了候选。
- **运行**：`offline_v1.sh` 末尾加 C2 一段，每臂 5 次，结果在 `results/c2/C_<臂>/<模型>/repN/`。峰位题 D 按设计不重跑。

### 2026-10-17 20:58 · 白板臂的远程目录不分模型：InPS4 的 Fable 臂作废重跑（基准自己的配置错，不是判分改动）

- **问题**：冻结的 `whiteboard/TASK_TEMPLATE.md` 第 44 行把远程目录写成 `{REMOTE_ROOT}/{MATERIAL}/`，同一材料的 Haiku 臂和 Fable 臂拿到同一个 LUMI 目录。
  InPS4 的 Fable 臂续跑时把 Haiku 臂留下的整套计算当成自己前一段的成果（20 个作业里 18 个是 Haiku 臂的），只自己算了 96³ 核。
- **核查其余臂**（作业号交集 + 转录里命令触及的远程子目录）：NbFeSb、KNbO3、MoS2、Bi2O2Se、CdS 的 Fable 臂发现别人的文件后另开子目录；GaP 两臂同时跑、各用子目录；
  SnS2 的 Haiku 臂把 Fable 第 1 段的目录挪进 `prior_attempt_archive/`，读了它的 Wannier 失败并记入 0.57 节点时"继承"作业（轻度信息泄漏，报告注明）。
- **处理**：InPS4 Fable 结果不计入（DECISION.log 10-17 20:50），原臂原样存到 `~/cophon_bench_whiteboard/v1/_invalid_shared_root/`。所有者批准重跑（10-17 晚）：
  任务单只改远程目录为 `.../bench_whiteboard_v1/InPS4_mp20790_fable/`，其余逐字相同；Claude Code 钉在其他 Fable 臂用的 2.1.302；LUMI 维护结束后由调度脚本启动。
- **模板不改**（改了会破坏 `FREEZE_v1.sha256`）；下一版模板的远程目录按臂分开：`{REMOTE_ROOT}/{MATERIAL}_{MODEL}/`。

### 2026-10-18 13:30 · 收尾核对（v1 按所有者 10-18 的决定结束，不涉及判分改动）

- **清单核对**：`FREEZE_v1.sha256` 112 个文件里 2 个与清单不符。`cophon_bench/run_models.py` 是 10-15 17:05 和 10-17 07:57 两条写过的额度提示修正；
  `kernel_pipeline/BASELINE.sha256` 是线 2 在 10-17 封存的 v2.0.14（Manneback 的 small 档改走公共分区，只改集群登记和一条路由测试，计算内容不变）。
  10-17 之后还在跑的 E 臂有没有作业走过这条路由，没有逐条核对；它只决定作业排到哪个分区。`FREEZE_v1_stage2.sha256` 27 个文件全部相符。
- **LUMI 关闭后的处理**（DECISION.log 10-18 07:10）：InPS4 白板 Fable 不重跑，记"作废"；Bi2O2Se 白板 Fable 由基准停下，64³ 临时结果单独判分、不计数；
  B 第 3 轮答案收齐、不判分。
- **B 第 3 轮一份答案超时**：Fable 第 1 次的 B_LiZnP_mp10182 在 900 秒时限内没有答完（没有内容），按同样设置（同一提示词、900 秒、同一运行器）重答一次。
  超时的原件留在 `results/b/_r3_timeout/`。
- **收尾用的脚本只做报表**：`e_close_v1.py`（每条臂调用冻结的 `pillar_e.py`，另出结局与成本台账）、`costs_v1.py`、`figures_v1.py`，都不改判定。
- **白板臂交付件复制进本目录**，做法同 v0：`whiteboard/arms/<材料>_<模型>/`，含任务书、笔记、报告、RESULT.json、作业日志、启动脚本、完整转录、
  输入与脚本（单个文件小于 1 MB），以及判分用的那个核文件；原始输出和论文 PDF 只留在本机 `~/cophon_bench_whiteboard/v1/`。
