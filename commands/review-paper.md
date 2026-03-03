---
name: review-paper
description: 自动化学术论文审稿。提供 PDF 路径即可启动完整审稿流程，支持按目标会议适配评审标准。
argument-hint: "<pdf_path> [--venue <conference>] [--with-code <code_dir>] [--with-supplement <sup_pdf>]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - TaskList
  - mcp__paper-parser__*
  - mcp__academic-search__*
---

# 自动化学术论文审稿

执行专业的学术论文审稿，按 4 个阶段完成多维度评审并输出结构化评审报告。支持按目标会议（CVPR/NeurIPS/ICML/ICLR/ECCV/ICCV/ACL/AAAI/KDD/MICCAI 等）动态调整评审策略。

## 参数解析

解析用户提供的参数：
- `<pdf_path>`：论文 PDF 路径（必须）
- `--venue <conference>`：目标会议/期刊（可选，如 CVPR, NeurIPS, ACL 等）
- `--with-code <code_dir>`：源代码目录路径（可选，启用代码审查）
- `--with-supplement <sup_pdf>`：补充材料 PDF 路径（可选）

如未指定 `--venue`，询问用户目标投稿会议。确认 PDF 文件存在后开始审稿流程。

## 会议适配策略

根据 `--venue` 参数加载对应的评审策略（参见 `references/venue-profiles.md`）：
- 调整评审维度权重（如 ICML 提高理论权重，CVPR 提高视觉效果权重）
- 加载会议特定的 Checklist 检查项
- 使用会议对应的评分标准和接收率参考
- 设定会议特定的基线和数据集期望

## Phase 1：论文解析

**方案 A（首选）：使用 Paper Parser MCP**

1. 调用 `paper_parser.parse_paper` 解析 PDF 为 Markdown
2. 调用 `paper_parser.extract_references` 提取参考文献列表
3. 调用 `paper_parser.extract_figures_and_tables` 提取图表和公式为 PNG 图像
4. 如有补充材料 PDF，同样解析
5. 使用 Read 工具读取提取的图表图像，进行视觉分析

**方案 B（Fallback）：MCP 不可用时直接读取 PDF**

如果 Paper Parser MCP Server 未启动或报错：
1. 使用 Read 工具直接读取 PDF 文件（Claude 支持多模态 PDF 阅读）
2. 逐页读取，每次最多 20 页：`Read(pdf_path, pages="1-10")` 然后 `Read(pdf_path, pages="11-20")`
3. 视觉分析图表和公式（直接从 PDF 页面图像分析）
4. 手动从文本中提取参考文献列表
5. 此模式下图表提取为 PNG 的功能不可用，但视觉分析仍然有效

**自动检测逻辑**：先尝试调用 `paper_parser.ping()`，如成功则用方案 A，如超时或报错则自动切换方案 B 并通知用户。

保存所有提取内容供后续阶段使用。

## Phase 1.5：速读评估（Quick Assessment）

在深度评审之前，进行全局质量速读判断（模拟资深审稿人的第一遍阅读）。

**自动化检查**：运行速读评估脚本获取量化指标：
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/quick-assess.py <parsed_text_file>
```

脚本自动检测以下指标：

1. **论文类型识别**：理论型 / 实验型 / 应用型 / 系统型（基于关键词频率）
2. **引用时效性统计**：
   - 近 2 年论文占比（≥25% 为良好，15-25% 偏旧，<15% 严重过时）
   - 中位引用年份
   - 年份分布直方图
3. **结构完整性检查**：自动检测是否包含 Abstract, Introduction, Related Work, Method, Experiments, Conclusion, Limitations, Broader Impact, References
4. **匿名化合规检查**：检测 GitHub 链接、"our previous work" 表述、代码公开声明
5. **统计严谨性检测**：自动扫描 ± 符号、error bars、多次运行、统计检验、置信区间、随机种子
6. **效率指标检测**：自动扫描 Params、FLOPs、FPS、内存、训练时间
7. **会议 Checklist 合规检查**（如指定了 venue）：
   - NeurIPS: Reproducibility Checklist, Broader Impact Statement
   - ACL: Responsible NLP Checklist (Section A-E), Limitations section
   - MICCAI: Ethics/IRB 声明, 临床价值说明
   - ICLR: 公开审稿格式合规

**输出**：初步印象 + 各项量化指标 + 审查重点建议，指导 Phase 2 的 Agent 设定侧重点。

## 审稿人视角加载

根据 `--venue` 参数加载对应会议的资深审稿人视角文档（如存在）：
- CVPR/ICCV → 读取 `docs/reviewer-perspectives/01-cvpr-reviewer.md` 或 `03-iccv-reviewer.md`
- NeurIPS → 读取 `docs/reviewer-perspectives/02-neurips-reviewer.md`
- ICML → 读取 `docs/reviewer-perspectives/05-icml-reviewer.md`
- ACL → 读取 `docs/reviewer-perspectives/07-acl-reviewer.md`
- 其他会议类推

将审稿人视角中的「最看重的维度」「该会议的审稿文化」「独特审稿技巧」融入后续 Phase 2 的评审过程。例如：
- CVPR 审稿人强调「视觉结果质量」→ Agent 需重点分析可视化结果
- ICML 审稿人强调「证明严谨性」→ Agent B 需逐行检查证明
- ACL 审稿人强调「LLM 基线」→ Agent C 需检查是否包含 LLM 对比

## Phase 2：并行多维度评审

启动并行 Agent 进行以下评审维度，每个 Agent 接收解析后的论文文本和相关数据。

### Agent A：摘要与动机 + 新颖性（维度 1-2）
评估：
- 研究空白是否有证据支撑？
- 核心概念是否形式化定义？
- 真正的新颖性 vs 已知技术组合？
- 声称的贡献与实际技术内容是否匹配？

### Agent B：技术正确性（维度 3）
使用提取的公式评估：
- 逐个检查公式的数学正确性（值域、符号一致性）
- 符号定义是否完整且一致
- 假设是否明确声明并有合理性
- 公式之间是否有逻辑矛盾
- 视觉检查提取的公式图像

### Agent C：实验 + 统计严谨性 + 竞品论文对比（维度 4）
使用提取的表格和 SOTA 数据评估：
- 调用 `academic_search.find_competing_methods` 获取 SOTA 排行榜和竞争方法
- 调用 `academic_search.get_sota_results` 获取每个主要基准的排行数据
- 基线是否最新？与 SOTA 排行榜对比
- **竞品论文深度对比**（最近 12 个月内的最相关论文）：
  1. 从论文中提取核心 task（如 "change detection"）和 dataset（如 "LEVIR-CD"）
  2. 调用 `academic_search.search_related_work` 搜索最近 12 个月内的相关论文
  3. 调用 `academic_search.find_competing_methods` 匹配相同 task+dataset 的竞争方法
  4. 使用 WebSearch 补充搜索：`"{task}" "{dataset}" {current_year}` 获取最新结果
  5. 生成竞品对比表：方法名、发表时间、核心技术路线、性能指标、与本文的差异
  6. 评估：论文对比的基线是否覆盖了这些最新竞品？遗漏了哪些？
- **实验公平性深度分析**：
  - 比较条件是否一致（相同骨干网络、训练数据、数据增强、epoch）
  - 表格脚注中是否隐藏了有利条件
  - 是否使用了官方基线实现和推荐超参
  - 是否 cherry-pick 了有利的对比设置
- 消融实验是否完整？（所有模块组合？消融数值加和是否合理？）
- **统计严谨性检查**：
  - 结果是单次运行还是多次平均？
  - 是否有 error bars / 标准差 / 置信区间？
  - 性能提升是否具有统计显著性？
  - 对于 NLP 论文：是否有 bootstrap test / Bonferroni 校正？
- 是否报告了效率指标（参数量、FLOPs、FPS）？
- 视觉检查提取的结果表格图像

### Agent D：写作质量 + 可复现性（维度 5-6）
评估：
- 语法和拼写错误（列出所有发现的）
- 全文符号一致性
- 是否有清晰的相关工作章节
- 实现细节是否足以复现
- 结论是否充分（局限性、未来工作）

### Agent E：相关工作 + 参考文献审计 + 遗漏检测（维度 7）
使用 Academic Search MCP 工具 + Web 搜索：
1. 调用 `academic_search.verify_references_batch` 验证所有参考文献
2. 调用 `academic_search.find_missing_citations` 检测遗漏引用
3. **主动搜索最近 12 个月的高引论文**：
   - 从论文中提取 3-5 个核心关键词
   - 使用 `academic_search.search_related_work` 搜索（year_range 设为最近 12 个月）
   - 使用 WebSearch 补充搜索 arXiv 和 Google Scholar 上的最新预印本
   - 按引用数排序，识别论文是否遗漏了高影响力的最新工作
4. 检查领域内近年关键工作是否被引用
5. 验证引用是否存在错配（错误的论文被分配到错误的名称）
6. **输出竞品论文清单**：列出最相关的 5-10 篇最新论文，标注论文是否已引用

## Phase 3：代码审查（可选）

如提供了 `--with-code`：
1. 系统性阅读源代码文件
2. 与论文公式交叉验证（检查每个方程是否与实现匹配）
3. 查找未披露的训练策略（数据增强、深度监督等）
4. 检查论文-代码不一致：
   - 激活函数
   - 损失函数权重
   - 架构细节（层数、卷积核大小）
   - 优化器和超参数

## Phase 4：报告生成

合并所有阶段输出为标准评审格式。

报告模板参见 Skill 中的 `references/review-template.md`。
评分标准参见 `references/scoring-guide.md`。
会议特定标准参见 `references/venue-profiles.md`。

报告中应包含：
- **速读印象**（来自 Phase 1.5）
- **多维度详细评审**（来自 Phase 2）
- **代码审查**（来自 Phase 3，如适用）
- **审稿人置信度**（1-5）
- **会议特定的评分映射**（如指定了 venue）
- **Meta-Review 级别的总结**

将报告保存到 PDF 同目录下，文件名 `Review_Report_[论文名].md`。
