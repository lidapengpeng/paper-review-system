---
name: 学术论文审稿
description: >-
  This skill should be used when the user asks to "审稿", "review paper",
  "审阅论文", "评审论文", "paper review", "检查论文质量",
  provides a PDF path for academic review, mentions "学术审稿",
  "conference review", "期刊审稿", or wants to evaluate an academic paper's
  quality across multiple dimensions including novelty, technical soundness,
  experiments, and writing quality.
version: 1.0.0
---

# 学术论文自动化审稿

## 概述

提供专业的学术论文自动化审稿能力，覆盖 8 个评审维度，集成 PDF 解析、参考文献验证、SOTA 对比和代码审查。适用于 AI/ML 会议论文和期刊投稿的审稿场景。

## 审稿流程

### Phase 1：论文解析
使用 Paper Parser MCP 将 PDF 转为结构化数据：
- 全文 Markdown（含 LaTeX 公式恢复）
- 图表提取为 PNG（用于视觉分析）
- 参考文献解析为结构化条目
- 论文元数据（标题、作者、摘要、章节大纲）

### Phase 2：8 维度并行评审
启动 5 个并行 Agent，覆盖 8 个评审维度：

| Agent | 维度 | 关键检查点 |
|-------|------|-----------|
| A | 摘要与动机 + 新颖性 | 研究空白、动机强度、创新性 |
| B | 技术正确性 | 公式验证、符号一致性、逻辑性 |
| C | 实验 | 基线对比、SOTA 排行、消融实验、统计显著性 |
| D | 写作质量 + 可复现性 | 语法、符号一致性、实现细节 |
| E | 相关工作 + 参考文献审计 | 参考文献验证、遗漏引用检测 |

### Phase 3：代码审查（可选）
当提供源代码时，检查论文-代码一致性：
- 公式与实现的对应关系
- 未披露的训练策略
- 架构细节差异

### Phase 4：报告生成
合并所有评审结果，按标准格式输出评审报告，包含：
- 优点/缺点总结
- 参考文献审计结果
- SOTA 对比分析
- 8 维度详细评分（1-5 分）
- 给作者的问题
- 接收建议

## MCP 工具说明

### Paper Parser MCP
| 工具 | 用途 |
|------|------|
| `parse_paper` | PDF → Markdown（支持 pymupdf/marker 引擎） |
| `extract_references` | 提取并解析参考文献 |
| `extract_figures_and_tables` | 图表/公式裁剪为 PNG |
| `get_paper_metadata` | 提取论文元数据 |

### Academic Search MCP
| 工具 | 用途 |
|------|------|
| `verify_references_batch` | 批量验证参考文献（CrossRef + DBLP） |
| `find_missing_citations` | 检测遗漏的重要引用 |
| `find_competing_methods` | 查找竞争方法和 SOTA 排行 |
| `get_sota_results` | 获取特定任务/数据集的 SOTA 结果 |
| `search_related_work` | 搜索相关论文 |

## 评审原则

1. **证据驱动**：每个评价必须引用论文中的具体内容作为支撑
2. **建设性**：指出缺点时同时给出改进建议
3. **公平性**：基于论文实际内容评价，不预设偏见
4. **全面性**：8 个维度缺一不可
5. **可验证**：参考文献和 SOTA 对比使用 API 自动验证

## 附属资源

### 参考文件
- **`references/review-template.md`** - 评审报告完整模板
- **`references/scoring-guide.md`** - 评分标准和接收建议指南
