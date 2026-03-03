# 评审报告模板

```markdown
# Review Report

**Paper**: [论文标题]
**Venue**: [目标会议/期刊]
**Review Date**: [审稿日期]

---

## Summary
[3-5 句话概述：论文做了什么、核心方法、关键结果]

## Strengths
[S1-S7: 具体优点，引用论文中的证据]

## Weaknesses
[W1-W5: 主要缺点，附带具体改进建议]

## Reference Audit
### Verification Results
| # | Title | Status | Discrepancies |
|---|-------|--------|---------------|
| 1 | ...   | Match/Mismatch/Not Found | ... |

### Missing Important Citations
[应该引用但未引用的论文列表，附原因]

## SOTA Comparison
### Competing Methods
[自动获取的 SOTA 排行榜]

### Analysis
[论文方法与 SOTA 对比分析，遗漏的基线]

## Competitive Paper Analysis (最近 12 个月)
### 最相关竞品论文
| # | 论文标题 | 发表时间 | 会议/期刊 | 核心技术路线 | 本文是否引用 |
|---|---------|---------|----------|------------|-----------|
| 1 | ... | YYYY-MM | ... | ... | 是/否 |

### 技术路线对比
[本文方法 vs 最强竞品的技术路线差异分析：
- 架构设计差异
- 损失函数差异
- 训练策略差异
- 性能对比（如有相同数据集的结果）]

### 遗漏的重要基线
[论文未对比但应该对比的最新方法，附理由]

## Detailed Comments
### 1. Abstract & Motivation (Score: X/5)
[详细评价]

### 2. Novelty (Score: X/5)
[详细评价]

### 3. Technical Soundness (Score: X/5)
[详细评价]

### 4. Experiments (Score: X/5)
[详细评价]

### 5. Writing Quality (Score: X/5)
[详细评价]

### 6. Reproducibility (Score: X/5)
[详细评价]

### 7. Related Work (Score: X/5)
[详细评价]

### 8. Supplementary Material (Score: X/5)
[详细评价]

## Code Audit (if applicable)
### Paper-Code Discrepancies
[论文与代码的不一致之处]

### Undisclosed Components
[代码中有但论文未提及的组件]

### Technical Correctness Issues
[代码实现中的技术问题]

## Minor Issues
[编号列表：语法、拼写、格式问题]

## Questions for Authors
[Q1-Q10+: 需要作者回答的关键问题]

## Overall Assessment
| Dimension | Score | Brief |
|-----------|-------|-------|
| Abstract & Motivation | X/5 | ... |
| Novelty | X/5 | ... |
| Technical Soundness | X/5 | ... |
| Experiments | X/5 | ... |
| Writing Quality | X/5 | ... |
| Reproducibility | X/5 | ... |
| Related Work | X/5 | ... |
| Supplementary Material | X/5 | ... |
| **Overall** | **X/5** | |

### Acceptance Recommendation
- [ ] Strong Accept / Accept / Weak Accept / Borderline / Weak Reject / Reject / Strong Reject

### Confidence Level
- [ ] 5 (Expert) / 4 (Confident) / 3 (Fairly confident) / 2 (Uncertain) / 1 (Low)

### Summary Comment
[最终总结段落]
```
