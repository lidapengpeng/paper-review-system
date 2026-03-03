---
name: 学术论文审稿
description: >-
  This skill should be used when the user asks to "审稿", "review paper",
  "审阅论文", "评审论文", "paper review", "检查论文质量",
  provides a PDF path for academic review, mentions "学术审稿",
  "conference review", "期刊审稿", or wants to evaluate an academic paper's
  quality across multiple dimensions including novelty, technical soundness,
  experiments, and writing quality. Supports venue-specific review for
  CVPR, NeurIPS, ICML, ICLR, ECCV, ICCV, ACL, AAAI, KDD, MICCAI and more.
version: 2.0.0
---

# 学术论文自动化审稿

## 概述

提供专业的学术论文自动化审稿能力，融合 10 个顶级 CS 会议（CVPR/NeurIPS/ICML/ICLR/ECCV/ICCV/ACL/AAAI/KDD/MICCAI）资深审稿人的审稿方法论。支持按目标会议动态调整评审策略、维度权重和 Checklist 检查。

## 核心升级（v2.0）

相比 v1.0 的关键改进：
1. **会议适配**：`--venue` 参数动态调整评审策略
2. **速读阶段**：Phase 1.5 全局质量快速评估
3. **统计严谨性**：error bars、多次运行、统计检验
4. **Checklist 合规**：会议特定的 checklist 自动检查
5. **实验公平性深度分析**：训练条件一致性、隐藏优势检测
6. **置信度评分**：审稿人置信度 1-5
7. **会议评分映射**：适配不同会议的评分标准

## 审稿流程（4 阶段）

### Phase 1：论文解析
使用 Paper Parser MCP 将 PDF 转为结构化数据。

### Phase 1.5：速读评估（新增）
模拟资深审稿人的"第一遍速读"：
- 识别论文类型（理论/实验/应用/系统）
- 30 秒质量信号检测（图表密度、引用时效、结构完整性）
- 会议 Checklist 合规快检
- 输出初步印象，指导后续评审重点

### Phase 2：多维度并行评审
5 个并行 Agent 覆盖评审维度（权重按目标会议调整）：

| Agent | 维度 | 关键检查点 |
|-------|------|-----------|
| A | 摘要与动机 + 新颖性 | 研究空白、动机强度、创新性判定 |
| B | 技术正确性 | 公式验证、符号一致性、证明严谨性 |
| C | 实验 + 统计严谨性 | SOTA 对比、公平性分析、error bars、统计检验 |
| D | 写作质量 + 可复现性 | 语法、符号一致、Limitations section |
| E | 相关工作 + 参考文献审计 | 参考文献验证、遗漏引用、引用质量分析 |

### Phase 3：代码审查（可选）
检查论文-代码一致性、未披露训练策略。

### Phase 4：报告生成
合并所有阶段结果，包含置信度评分和会议特定评分映射。

## 会议适配机制

通过 `--venue` 参数自动加载会议审稿策略（详见 `references/venue-profiles.md`）：
- **维度权重**：如 ICML 理论权重 35%，CVPR 新颖性权重 35%
- **Checklist**：NeurIPS Reproducibility / ACL Responsible NLP / MICCAI Ethics
- **评分映射**：适配会议的实际评分标准（如 NeurIPS 1-10 → 系统 1-5）
- **基线期望**：会议特定的必须对比方法和数据集

## 评审原则

1. **证据驱动**：每个评价引用论文具体内容
2. **建设性**：缺点必须附带改进建议
3. **公平性**：基于实际内容，不预设偏见
4. **会议感知**：按目标会议标准评审
5. **统计意识**：关注实验的统计严谨性
6. **可验证**：参考文献和 SOTA 使用 API 自动验证

## 附属资源

### 参考文件
- **`references/review-template.md`** - 评审报告完整模板
- **`references/scoring-guide.md`** - 评分标准和接收建议指南
- **`references/venue-profiles.md`** - 10 个顶会的审稿策略配置（新增）

### 审稿人视角文档
`docs/reviewer-perspectives/` 目录包含 10 位顶会资深审稿人的详细方法论：
- `01-cvpr-reviewer.md` ~ `10-miccai-reviewer.md`
- `00-synthesis-and-upgrade-plan.md` - 综合分析与升级方案
