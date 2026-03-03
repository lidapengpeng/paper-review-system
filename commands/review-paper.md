---
name: review-paper
description: 自动化学术论文审稿。提供 PDF 路径即可启动完整审稿流程。
argument-hint: "<pdf_path> [--with-code <code_dir>] [--with-supplement <sup_pdf>]"
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

执行专业的学术论文审稿，按 4 个阶段完成 8 维度评审并输出结构化评审报告。

## 参数解析

解析用户提供的参数：
- `<pdf_path>`：论文 PDF 路径（必须）
- `--with-code <code_dir>`：源代码目录路径（可选，启用代码审查）
- `--with-supplement <sup_pdf>`：补充材料 PDF 路径（可选）

确认 PDF 文件存在后开始审稿流程。

## Phase 1：论文解析

使用 Paper Parser MCP 工具提取结构化内容：

1. 调用 `paper_parser.parse_paper` 解析 PDF 为 Markdown
2. 调用 `paper_parser.extract_references` 提取参考文献列表
3. 调用 `paper_parser.extract_figures_and_tables` 提取图表和公式为 PNG 图像
4. 如有补充材料 PDF，同样解析
5. 使用 Read 工具读取提取的图表图像，进行视觉分析（架构图、结果表格）

保存所有提取内容供后续阶段使用。

## Phase 2：并行 8 维度评审

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

### Agent C：实验（维度 4）
使用提取的表格和 SOTA 数据评估：
- 调用 `academic_search.find_competing_methods` 获取 SOTA 排行榜和竞争方法
- 调用 `academic_search.get_sota_results` 获取每个主要基准的排行数据
- 基线是否最新？与 SOTA 排行榜对比
- 比较是否公平？（相同骨干网络、相同训练数据？）
- 消融实验是否完整？（所有模块组合？）
- 结果是单次运行还是多次平均？
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

合并所有 Agent 输出为标准评审格式。

报告模板参见 Skill 中的 `references/review-template.md`。
评分标准参见 `references/scoring-guide.md`。

将报告保存到 PDF 同目录下，文件名 `Review_Report_[论文名].md`。
