# cophon-bench v1 · 设计（2026-10-15 起草；所有者同意方案；10:30 所有者放行 HPC——v2.0.12 调度规则 Q1 已上线；本文随进展更新）

**一句话**：v1 不加新题。把 v0 最强的结论（端到端）从"推断"变成"测量"，把最弱的一环补上，堵住 v0 自己发现的判分漏洞，做到外人能复跑。
**状态（2026-10-15 11:00）**：冻结已写（`FREEZE_v1.sha256` 112 个文件、`FREEZE_NOTE.md`，harness = kernel_pipeline v2.0.12）；26 个材料在基准库里跑
（16 条端到端 harness 臂 + 10 个扩池材料，监督器单元 `cophon-bench-v1-e2e`，工单中继单元 `cophon-bench-v1-relay`）；离线题 A 在跑（`cophon-bench-v1-offline-claude/-deepseek`）；
白板臂 16 个沙箱任务目录就位，等所有者启动（`~/cophon_bench_whiteboard/_sandbox/README.md`）。所有者 10:30 的三条指示：HPC 调度策略已更新、完成后续基准；docker 给命令；
离线重跑现在就开、与所有者的 Claude 使用并行、尽量不触发额度限制。

## 1. 目标与所有者裁决

同 v0 的两个角度：(1) harness 加 Claude 比白板 Claude 强；(2) harness 把最便宜的模型抬到前沿模型单干的水平。
所有者 10-15 的裁决（DECISION.log 2026-10-15 08:25）：
- 同意 v1 主张；端到端材料加到 **8 个**。
- **HPC 使用整体 on hold**：所有者在另一处调查统一智能调度，有结论再通知；先做不需要集群计算的部分。
- **基准不改 harness**：v0 发现的三处 harness 不足（晶胞静默退回、打包作业每步超时、Wannier 墙钟估计）属于线 2，基准只记录并交接
  （`records/handoffs/2026-10-15-bench-v0-harness-findings-for-line2.md`）；v1 开跑前封当时的 kernel_pipeline 版本号，测到什么报什么。
  多峰判分与"把晶胞封进题目"是基准自己的改动。

## 1b. 10-15 上午开跑时的操作决定（agent 定，所有者可改）

- **端到端新材料**：所有者没有另选，按建议取 CdS、KNbO3、MoS2 单层、InPS4、Bi2O2Se（备选 LiAsS2、VFeSb 的基线也封了，换材料只损失已跑的 harness 臂算力）。
- **集群**：端到端 harness 臂 16 个材料固定 `--cluster lumi`（基线与白板臂都在 LUMI，工具链一致，墙钟可比；LUMI 之内的分区路线仍由 Q1 选）。
  扩池 10 个材料用 Q1 的默认 auto，全部选了 Manneback（预计等待 0 小时、费用权重 0.2）——这同时是 Q1 在真实负载下的观察样本（线 2 10-22 复看）。
  第一次建的 16 个端到端材料也都被 auto 选到 Manneback（每个材料单独探测、都看到空队列），为上面的理由重建到 LUMI；没有提交过作业。
- **名字**：`<材料>_e2eH`（harness+Haiku）、`<材料>_e2eF`（harness+Fable）、`<材料>_cx`（扩池，Haiku 操作）；同名材料不能与真材料库共用远端目录，所以都带后缀。
- **harness 臂的工单**：中继每 5 分钟跑一遍，操作员模型按后缀选；校验通过且不是升级的答案由监督器应用（零人工）；升级（escalate）与连续三次无效答案留给人，
  每条算一次人工触碰（`results/e/relay/ESCALATIONS.md`）。v1 不跑影子模型。
- **离线重跑**：主集 5 次 = v0 的 3 次（提示词逐字节相同）+ 新 2 次；留出集 5 次新跑；Claude 一次一个调用、每次前停 20 秒、额度用尽等 20 分钟再试；DeepSeek 走 API 另开一路。
- **白板沙箱**：<user> 已在 docker 组（无需 sudo）；镜像 `cophon-bench-wb:v1`（node:22-slim + ssh/rsync/python3/numpy/pdftotext，uid 1002）；容器里只有任务目录、
  只读的 LUMI ssh 身份、只读的赝势表；`claude` 二进制只读挂载；订阅凭据用 `claude setup-token` 的无头令牌（所有者在自己终端生成，放
  `<private>`）。本会话能验证的：镜像里 `claude --version`、工具齐、只见工作目录；API 路径通（假令牌得到 api_error）。
  没能验证的：容器内 `ssh lumi`（本会话的权限分类器不让挂载私钥测试）——第一条白板臂启动时看 `stderr.log`。
- **B 第 3 轮**：137 份提示词已生成（15 个模型/重复里前两轮没过的材料），排在离线队列 A 之后；打分的打包作业等模型答完再提（`COPHON_BENCH_VERSION=v1`）。
  新难材料不另算：从本次飞行里取 d 壳层材料（TiPbO3、KNbO3、MoS2）的 superset 阶段数据，飞行后再定。

## 2. 与 v0 的差别一览

| 项 | v0 | v1 | 为什么 |
|---|---|---|---|
| 端到端臂 | harness+Haiku、白板 Fable（harness+Fable 用影子推断） | **2×2**：harness+Haiku、harness+Fable、白板 Fable、**白板 Haiku** | 把"harness+Fable 等价"从推断变测量；补"低端模型单干做不出来"这一格 |
| 端到端材料 | 3（GaP、SnS2、NbFeSb） | **8**（3 旧 + 5 新，候选 `design/E_candidates.md`） | 样本量；按难度维度挑（纤锌矿低频模、钙钛矿、2D、低对称、近半金属层状） |
| 题目输入的晶胞 | 各臂自己弛豫/查找 | **封存的生产晶胞**发给两臂（`labels/cells/`），只松弛内坐标 | SnS2 三个晶胞三个峰位；基线与两臂必须同一晶胞 |
| 端到端判分 | 单一全局最大值 ±0.15 eV | **前两个峰**：臂的主峰落在基线前两峰之一的 ±0.15 eV，峰高按该峰 ±25%，模式组频率 ±5%；另记谱的整体偏差 | SnS2 双峰等高，最大值随晶胞翻转 |
| 端到端交付 | 报告里的数 + 事后手工重算 | **RESULT.json 合同** + 核文件固定路径；判分器重算，自报偏差单列 | 代码判，不手工 |
| 墙钟 | 排队吃掉 7.5 小时，不可比 | 分区**按队列选**（流水线 v2.0.3 起支持），墙钟进表 | 让墙钟变成可测的指标 |
| 运维题 A | 44 张（19 封存 + 25 活工单） | 44 张 + **时间留出集** H01–H07（冻结后新飞行的工单，到 v1 冻结前继续长） | 堵"规则是照着这些票调的"的质疑 |
| 重复次数 | 3 | **5**（离线题） | 中位数更稳 |
| Wannier 题 B | 16 材料两轮 | 第 3 轮 + **2–4 个新难材料**（d 壳层/空隙态类） | NbFeSb 的教训进了策略，必须在新材料上验，不能只在 NbFeSb 上验 |
| 选材题 C | 池子是循环按旧 prior 挑出来算的 | **扩池**：从有 prior 没核的材料里按阴离子分层随机抽 10 个新算核（`design/C_expansion_sample.json`） | 去掉池子偏向；这批飞行同时给 E 的 harness+Haiku 臂加 10 个无人值守样本 |
| 峰位题 D | 一根柱子 | 保留为**阴性对照**（附录），不再花钱 | "harness 不擅长什么"本身增加可信度 |
| 白板隔离 | 任务书禁区 + 转录审计 | 争取**容器沙箱**（docker 组，需所有者 sudo）；拿不到则沿用 v0 并如实写 | 审计不是隔离 |
| 外部复跑 | 无 | 公开仓库放"从公开答案表重判"的脚本与说明；白板臂可复跑，harness 臂只能复核（提示词与规则不公开） | 可信度 |
| 模型 | 五个 | 离线题沿用五个（Haiku 5.5 / Sonnet 5.5 / Opus 5.5 / Fable 5.1 / DeepSeek v4 flash）；端到端只用 Haiku 与 Fable | 省钱，端到端的问题是 2×2 |

## 3. 五题设计

### A 运维决策
- 主集：v0 的 44 张不变（`kernel_pipeline/bench/tickets/T*.json` 19 张 + `cophon_bench/tickets_ext/X*.json` 25 张）。
- 留出集：`cophon_bench/tickets_holdout/H*.json`，由 `cophon_bench/holdout_build.py` 从 2026-10-14 12:04（v0 冻结）之后的活工单生成，标签只来自记录
  （state.json 的后续、答复文件、日志、提交说明）。今天 7 张：NbFeSb_mp9437_kpm 的 4 张（卡片提案 IT7、同轮重提、sbatch 布局拒绝、EPW1 门失败=构造缺陷）、
  NbFeSb_mp9437_kp 与 CdS_mp672_kp 的 2 张异常工单（diagnose）、CdS_mp672_kp 的 1 张分析代码缺陷。到 v1 冻结前再跑一次脚本收新票。
- 判分器 `pillar_a.py` 加了 `--holdout`：主集与留出集各出一张表；主集在 v0 结果上重判与 v0 表逐数一致（回归检查 2026-10-15）。
- 重复 5 次；两臂提示词不变。

### B Wannier 投影
- 第 3 轮：每个模型拿自己前两轮的块与打分再答一次（`b_round2.py` 的机制延一轮）。
- 新难材料 2–4 个：从 d 壳层 + 空隙态一类里挑（候选待定：要有 10-12 实验的重叠矩阵或新算一次电子阶段——后者要 HPC）。
- 打分要集群（串行 wannier90 打包作业）：**on hold**。打包作业的每步超时属于基准自己的运行时（`b_runtime/`），不在 harness 交接单里，v1 开跑前改。

### C 选材
- 扩池名单 `design/C_expansion_sample.json`：抽样框 = 有 prior、没有封存核、无 BLOCKED 阶段、prior 成本估计 ≤ 10 节点时的材料（78 个）；
  按化学式最后一个元素分层、比例分配、层内均匀抽样，种子 20261015，抽 10 个；**从不读 prior 分**（成本过滤是预算约束，已披露）。
  今天的抽样：Be2C、Ca2NCl、SnI4、NaPN2、AlN、TiPbO3、AlAsO4、Al2CdS4、LiZnPS4、CdTe，prior 成本估计合计 52 节点时。
- 算核：harness+Haiku 无人值守飞行（`cophon --library cophon-bench-v1/e2e_library supervise`），**on hold**。算完后重新冻结 C 的标签与候选池。
- 判分不变（`pillars_cd.py`）。

### D 峰位预测
- 题目、判分不变；不再新跑模型；报告里作为阴性对照一节。

### E 端到端
- **臂**：harness+Haiku、harness+Fable、白板 Fable、白板 Haiku。白板臂由所有者启动（无头会话；本会话只准备任务书与一行命令）。
- **材料**：8 个，候选与基线见 `design/E_candidates.md`；基线由 `cophon_bench/pillar_e.py baselines` 从库里封存的核文件重算并封进 `labels/E_baselines.json`。
- **封存输入**（两臂相同）：`labels/cells/<材料>.cif` 与 `.POSCAR`（基线的生产晶胞）；任务书规定晶胞不得改动，只松弛内坐标。
  harness 臂的对应用法：`cophon new <M> --cif labels/cells/<M>.cif --relax fixed --cell-policy pbesol`。**预检已做**（2026-10-15，隔离的临时材料库，不提交）：
  intake 记 `relax: fixed`、`production_cell: input`、`measured_cell: None`（不查 COD），dry-run 渲染的 relax 输入卡是 `calculation = 'relax'`（只松弛内坐标）并带给定的
  CELL_PARAMETERS；真材料库未被触碰。白板臂：任务书模板 `whiteboard/TASK_TEMPLATE.md`。
- **交付合同**（白板臂写、harness 臂由判分器从材料库生成）：`RESULT.json`
  `{"schema":"cophon-bench.e.result.v1","material":…,"kernel_file":"kernel/Gamma_alphabeta_s.dat","peak_ev":…,"peak_a2_per_ev":…,"mode_thz":…,"mode_irrep":…,"mesh":…,"cell_angstrom":[[…]],"node_hours":…,"wall_hours":…,"model_usd":…,"human_touches":…}`，
  核文件按代码原样放在 `kernel_file` 指的路径。
- **判分**（`pillar_e.py grade`，纯代码）：臂的核文件用流水线自己的解析器（`kernel_pipeline.lib.epw.parse_kernel`、`kernel_invariant`）重算不变量谱；
  "同一答案" = 主峰落在基线前两峰之一的 ±0.15 eV 内 **且** 峰高在该基线峰的 ±25% 内 **且** 峰处最强模式组的频率在 ±5% 内。
  另记：谱的整体偏差（插到基线网格上，最大绝对偏差/基线最大值，相对 L2）、第二峰是否也对上、自报数与重算的偏差、臂实际用的晶胞与封存晶胞的偏差（%）、
  节点时（sacct CPUTimeRAW/128，同 v0 口径）、墙钟、人工触碰、模型费。
- **判分器自检**（已做，`design/regrade_v0_with_v1_rule/E_table.md`）：用 v1 规则重判 v0 的六条飞行——harness 臂三个全部"同一答案"（SnS2 对上基线的第二峰 3.78 eV，
  峰高 +5.7%，模式 −1.8%；v0 规则下它是"不同答案"），白板 GaP、NbFeSb 同一答案，白板 SnS2 仍不同（4.08 eV 不在两峰任一 ±0.15 内——晶胞 c = 6.229 Å，正是 v1 封晶胞要消除的）。
  晶胞偏差一栏把 SnS2 harness 臂 c 轴 +3.2% 标了出来。
- **上限**：harness 臂每材料 ≤ 2× 基线节点时且 ≤ 10 节点时；白板臂每条 ≤ 20 节点时、$120、600 轮、3 天（同 v0）。
- **分区**：两臂按队列感知选分区（harness 臂是流水线 v2.0.3 的功能；白板臂任务书给出各分区的说明）。
- **harness 版本**：开跑时封当时的 kernel_pipeline 版本——**v2.0.12**（2026-10-15 09:15 封存），`FREEZE_NOTE.md` 已写。

## 4. 隔离

白板臂首选容器沙箱：本机有 docker，<user> 不在 docker 组（需所有者 `sudo usermod -aG docker <user>` 并重新登录）。容器只挂白板目录与 ssh 配置的只读副本，
无项目目录。拿不到就沿用 v0 的三道线（任务书禁区、独立目录、`logs/wb_audit.py` 转录审计）并在报告里写明"审计不是沙箱"。

## 5. 冻结与披露

顺序：设计定稿 → 标签（E_baselines、C 标签重冻结、留出集）与判分器（pillar_a/b/cd/e）sha256 进 `FREEZE_v1.sha256` → 任何模型或白板运行。
冻结后的任何改动写 `FREEZE_NOTE.md`，不悄悄刷新清单。v0 的表不回溯（v1 规则重判 v0 数据只作判分器自检，放 design/）。

## 6. 预算（估算，不是报价）

| 项 | 节点时 | 模型费 |
|---|---|---|
| E：5 个新材料 × 4 臂（harness 臂按基线 ~23 节点时 × 2 模型；白板臂按 v0 的 2.6–9.4 倍，上限 20/条） | 100–180 | 白板 Fable ≈ $33/材料 → ≈ $170；白板 Haiku 少 |
| E：3 个旧材料补 harness+Fable 与白板 Haiku 两臂 | 15–40 | ≈ $20 |
| C 扩池 10 个（prior 估计合计 52） | 40–60 | 很少 |
| B 第 3 轮 + 新材料 | 10–20 | ≈ $50 |
| A/C 离线重跑，5 模型 × 5 次（A 含留出集 51 张 × 2 臂） | 0 | ≈ $150 list 价；Claude 走订阅的 5 小时窗 |
| 合计 | **约 165–300**（v0 是 75） | **约 $400** |

## 7. 阶段与"要不要集群"

| 工作 | 要 HPC？ | 状态（2026-10-15） |
|---|---|---|
| 设计定稿、交接单、记录 | 否 | 本文；交接单已写 |
| E 判分器（前两峰、晶胞、交付合同）与自检 | 否 | 完成（`pillar_e.py`、`design/regrade_v0_with_v1_rule/`） |
| E 候选材料与基线封存（10 个候选） | 否 | 完成（`design/E_candidates.md`、`labels/E_baselines.json`、`labels/cells/`）；所有者定 5 个 |
| E 白板任务书模板 | 否 | 完成（`whiteboard/TASK_TEMPLATE.md`） |
| A 留出集（H01–H07）+ 判分器 `--holdout` + 回归 | 否 | 完成；冻结前再收一次 |
| C 扩池抽样名单 | 否 | 完成；算核 on hold |
| A 离线重跑（主集第 4–5 次 + 留出集 5 次） | 否（吃所有者的 Claude 订阅窗） | **在跑**（10:55 起，单元 `cophon-bench-v1-offline-claude` / `-deepseek`；节奏见 §1b） |
| C 离线重跑 | 否 | 等扩池出核、第二阶段冻结 |
| 可外部复跑的重判脚本与说明 | 否 | 待 |
| harness 臂 `--relax fixed` 预检（dry-run 渲染输入卡） | 否（dry-run 不提交） | 完成（见 §3 E） |
| B 第 3 轮：提示词 137 份 | 否 | 完成；模型答题排在离线队列 A 之后；打分（打包作业，每步超时）等答完 |
| C 扩池算核（10 个 `_cx`） | 是 | **在跑**（11:00 起，Manneback，Haiku 操作） |
| E harness 臂 16 条飞行 | 是 | **在跑**（11:00 起，LUMI，封存晶胞） |
| E 白板臂 16 条（沙箱） | 是 | 就位，等所有者启动（`~/cophon_bench_whiteboard/v1/wb_queue.sh`） |
| 报告 v1、公开仓库 publish_v1 | 否 | 等结果 |

## 8. 待所有者（2026-10-15 11:00 更新）

1. 在自己的终端生成无头令牌并启动白板队列：`~/cophon_bench_whiteboard/_sandbox/README.md`（`claude setup-token` → `<private>` → `bash ~/cophon_bench_whiteboard/v1/wb_queue.sh`）。
2. 若不同意 §1b 的 5 个新材料，在白板臂启动前说（harness 臂已在算，换材料只损失那两条飞行的算力）。
已解决：HPC 放行（10:30）；docker 组已在；离线重跑按节奏并行。

## 9. 目录

```
cophon-bench-v1/
  DESIGN.md                 本文
  design/                   E_candidates.md、C_expansion_sample.json、regrade_v0_with_v1_rule/（判分器自检）
  labels/                   E_baselines.json、cells/<M>.cif|.POSCAR（封存晶胞）；C/D 标签在扩池后重冻结
  whiteboard/               TASK_TEMPLATE.md、sandbox/Dockerfile；白板臂的工作目录在 ~/cophon_bench_whiteboard/v1/<材料>_<模型>/（飞行后复制交付件进来）
  e2e_library/              harness 臂与扩池的材料库（kernel_pipeline_bench.toml 配置、_library/ 案例库快照、E_TIMELINE.log、supervise_v1.log）
  prompts/                  A_harness、A_whiteboard（51 张）、B_whiteboard_r3/<模型>/<重复>/
  results/                  a/（第 1–3 次来自 v0）、b/（v0 两轮的提案与卡片 + 第 3 轮）、e/relay/（中继记录、ESCALATIONS.md）
  logs/                     new_materials.log、offline_*.log、relay_unit.log、wb_audit.py
  FREEZE_v1.sha256, FREEZE_NOTE.md；tables/ report/ 等结果
```
