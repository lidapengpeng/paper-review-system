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

使用 Paper Parser MCP 工具提取结构化内容：

1. 调用 `paper_parser.parse_paper` 解析 PDF 为 Markdown
2. 调用 `paper_parser.extract_references` 提取参考文献列表
3. 调用 `paper_parser.extract_figures_and_tables` 提取图表和公式为 PNG 图像
4. 如有补充材料 PDF，同样解析
5. 使用 Read 工具读取提取的图表图像，进行视觉分析（架构图、结果表格）

保存所有提取内容供后续阶段使用。

## Phase 1.5：速读评估（Quick Assessment）

在深度评审之前，进行全局质量速读判断（模拟资深审稿人的第一遍阅读）：

1. **论文类型识别**：理论型 / 实验型 / 应用型 / 系统型
2. **30 秒质量信号检测**：
   - 图表密度和质量（图表多且清晰 = 正面信号）
   - 参考文献时效性（近 2 年论文占比）
   - 论文结构完整性（是否有 Limitations, Broader Impact 等）
   - 数学符号规范度
3. **会议 Checklist 合规检查**（如指定了 venue）：
   - NeurIPS: Reproducibility Checklist, Broader Impact Statement
   - ACL: Responsible NLP Checklist (Section A-E), Limitations section
   - MICCAI: Ethics/IRB 声明, 临床价值说明
   - ICLR: 公开审稿格式合规
   - 通用: 匿名化检查（双盲是否合规）
4. **初步印象输出**：论文类型、质量水位预估、审查重点建议

此阶段的输出用于指导 Phase 2 的 Agent 设定审查侧重点。

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

### Agent C：实验 + 统计严谨性（维度 4）
使用提取的表格和 SOTA 数据评估：
- 调用 `academic_search.find_competing_methods` 获取 SOTA 排行榜和竞争方法
- 调用 `academic_search.get_sota_results` 获取每个主要基准的排行数据
- 基线是否最新？与 SOTA 排行榜对比
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

### Agent E：相关工作 + 参考文献审计（维度 7）
使用 Academic Search MCP 工具：
1. 调用 `academic_search.verify_references_batch` 验证所有参考文献
2. 调用 `academic_search.find_missing_citations` 检测遗漏引用
3. 检查领域内近年关键工作是否被引用
4. 验证引用是否存在错配（错误的论文被分配到错误的名称）

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
