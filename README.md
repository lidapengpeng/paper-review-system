# Paper Review System v2.2

学术论文自动化审稿系统 - Claude Code 插件。

融合 10 个 CS 顶会（CVPR/NeurIPS/ICML/ICLR/ECCV/ICCV/ACL/AAAI/KDD/MICCAI）资深审稿人的方法论，集成 PDF 解析、参考文献验证、SOTA 对比、竞品论文分析、代码审查，支持按目标会议动态适配评审策略。

## 功能特点

- **会议适配审稿**：`--venue CVPR` 自动调整评审维度权重和 Checklist 检查（支持 15+ 会议/期刊）
- **PDF 智能解析**：MCP 解析 + Claude 直接读取 PDF 双模式（MCP 不可用自动 fallback）
- **速读自动化**：自动检测引用时效性、结构完整性、匿名化合规、统计严谨性、效率指标
- **参考文献审计**：CrossRef + DBLP + Semantic Scholar 自动验证每条参考文献
- **竞品论文对比**：自动搜索最近 12 个月内最相关的竞争论文，生成技术路线对比表
- **SOTA 排行对比**：自动获取排行榜数据，检测遗漏的最新基线
- **8 维度评审**：摘要与动机、新颖性、技术正确性、实验+统计严谨性、写作质量、可复现性、相关工作、补充材料
- **代码审查**：可选的论文-代码一致性检查
- **并行评审**：5 个 Agent 并行处理
- **Rebuttal 辅助**：逐条起草 rebuttal 回复 + 验证修改稿是否回应审稿意见
- **快速预筛选**：1 分钟内输出论文量化质量信号，适合批量筛选

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 可选：配置 API Key

```bash
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"    # 加速参考文献验证
export CROSSREF_MAILTO="your-email@example.com"     # CrossRef polite pool
```

### 3. 开始使用

```bash
# 完整审稿（推荐指定目标会议）
/paper-review-system:review-paper /path/to/paper.pdf --venue CVPR

# 论文 + 代码审查
/paper-review-system:review-paper /path/to/paper.pdf --venue NeurIPS --with-code /path/to/code/

# 全部功能
/paper-review-system:review-paper /path/to/paper.pdf --venue ICML --with-code ./code/ --with-supplement ./supplement.pdf

# 快速预筛选（< 1 分钟，不做完整审稿）
/paper-review-system:pre-screen /path/to/paper.pdf --venue CVPR

# Rebuttal 辅助 - 起草回复
/paper-review-system:rebuttal /path/to/review_comments.md

# Rebuttal 辅助 - 验证修改稿
/paper-review-system:rebuttal /path/to/review_comments.md /path/to/revised_paper.pdf
```

## 审稿流程

```
Phase 1    → 论文解析（MCP 优先，Claude 直读 PDF fallback）
Phase 1.5  → 速读评估（自动化脚本：引用时效、结构、匿名化、统计、效率）
           → 审稿人视角加载（按 --venue 加载对应会议审稿人方法论）
Phase 2    → 5 Agent 并行多维度评审（维度权重按会议适配）
           → paper-comparator 自动搜索最近 12 个月竞品论文
Phase 3    → 代码审查（可选）
Phase 4    → 报告生成（含竞品对比表、置信度、会议评分映射）
```

## 支持的会议/期刊

| 类别 | 会议 |
|------|------|
| 计算机视觉 | CVPR, ICCV, ECCV, WACV |
| 机器学习 | NeurIPS, ICML, ICLR |
| 人工智能 | AAAI, IJCAI |
| NLP | ACL, EMNLP |
| 数据挖掘 | KDD |
| 多媒体 | ICME, ACM MM |
| 医学图像 | MICCAI |
| 期刊 | TPAMI, IJCV, TIP, TGRS 等 |

## 插件组件

| 组件 | 类型 | 功能 |
|------|------|------|
| `paper-review` | Skill | 审稿方法论 + 评分标准 + 会议策略 |
| `/review-paper` | Command | 完整审稿入口，支持 `--venue` 会议适配 |
| `/pre-screen` | Command | 快速预筛选（< 1 分钟，量化质量信号） |
| `/rebuttal` | Command | Rebuttal 辅助（起草回复 + 验证修改） |
| `paper-analyzer` | Agent | PDF 解析和结构分析 |
| `technical-reviewer` | Agent | 公式验证 + 实验分析 + 统计严谨性 |
| `reference-auditor` | Agent | 参考文献审计 + 遗漏引用检测 |
| `paper-comparator` | Agent | 竞品论文搜索 + 技术路线对比分析 |
| `paper-parser` | MCP Server | PDF → Markdown + 图表提取 |
| `academic-search` | MCP Server | 参考文献验证 + 学术搜索 |
| `check-deps.sh` | Hook Script | SessionStart 自动检查依赖 |
| `quick-assess.py` | Script | Phase 1.5 速读自动化检查 |

## 输出

### 审稿报告 (`Review_Report_[论文名].md`)

- 速读评估结果（引用时效、结构完整性、统计严谨性指标）
- 优点 / 缺点（引用论文具体证据）
- 参考文献审计（验证结果表 + 遗漏引用列表）
- SOTA 排行对比
- 竞品论文对比表（最近 12 个月最相关论文的技术路线对比）
- 8 维度详细评分（1-5 分，会议适配权重）
- 代码审查结果（如适用）
- 给作者的问题
- 审稿人置信度（1-5）
- 接收建议（Strong Accept → Strong Reject，含会议评分映射）

### 预筛选报告 (`PreScreen_[论文名].md`)

- 量化质量信号表（引用时效、结构、匿名化、统计、效率）
- 初步评估和审稿重点建议

### Rebuttal 文档 (`Rebuttal_[论文名].md` 或 `Revision_Check_[论文名].md`)

- 逐条审稿意见回复草稿（模式 A）
- 修改验证清单（模式 B）

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 本地测试
claude --plugin-dir /path/to/paper-review-system
```

## License

MIT
