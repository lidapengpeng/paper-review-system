---
name: rebuttal
description: 辅助撰写 rebuttal / 检查修改稿是否回应了审稿意见。
argument-hint: "<review_file> [revised_pdf] [--original <original_pdf>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - mcp__paper-parser__*
  - mcp__academic-search__*
---

# Rebuttal 辅助

帮助作者系统性地回应审稿意见，支持两种模式：

## 模式判断

根据参数自动选择模式：

- **模式 A（撰写 Rebuttal）**：只提供审稿意见文件 → 帮助逐条分析并起草回复
- **模式 B（修改验证）**：提供审稿意见 + 修改稿 → 逐条检查是否已充分回应

## 参数解析

- `<review_file>`：审稿意见文件路径（Markdown / 纯文本 / PDF），必须
- `[revised_pdf]`：修改后的论文 PDF（可选，模式 B）
- `--original <original_pdf>`：原始投稿 PDF（可选，用于对比修改前后差异）

## 模式 A：撰写 Rebuttal

### Step 1：解析审稿意见

从审稿文件中提取结构化信息：
1. 识别每位 Reviewer 的评审内容
2. 提取所有 Weakness（W1, W2, ...）
3. 提取所有 Questions（Q1, Q2, ...）
4. 提取评分和接收建议
5. 识别 Major vs Minor 问题

### Step 2：分类与优先级排序

将所有问题分为四类：
| 类型 | 说明 | 回复策略 |
|------|------|---------|
| **可直接回应** | 审稿人误解或论文已有说明 | 引用论文具体位置澄清 |
| **需要补充实验** | 缺少某个对比/消融 | 说明将补充的实验及预期结果 |
| **需要修改论文** | 写作、格式、引用问题 | 说明具体修改方案 |
| **根本性质疑** | 对方法/动机的根本性问题 | 需要最充分、最有说服力的回复 |

按影响力排序：根本性质疑 > 补充实验 > 修改论文 > 直接回应

### Step 3：逐条起草回复

为每条 Weakness 和 Question 生成回复草稿：

```markdown
## Response to Reviewer #X

### W1: [审稿人原文摘要]

**Response**: [回复内容]

**Action taken**: [具体修改说明，标注论文中的位置]
```

回复原则：
1. **先感谢**：感谢审稿人的建设性意见
2. **不回避**：正面回答每个问题，不绕弯子
3. **有证据**：每个回复附带具体证据（实验数据、论文引用、公式推导）
4. **标位置**：修改内容标注在论文中的具体位置（如 "Section 3.2, Eq.5"）
5. **不争辩**：即使审稿人有误解，也用事实和数据平和回应

### Step 4：生成 Rebuttal 文档

输出完整的 rebuttal 文档，保存为 `Rebuttal_[论文名].md`：

```markdown
# Rebuttal

We thank all reviewers for their constructive feedback.

## Summary of Changes
[主要修改概述]

## Response to Reviewer #1
### W1: ...
### Q1: ...

## Response to Reviewer #2
...

## Additional Experiments (if applicable)
[补充实验结果表格]
```

### Step 5：补充实验建议

如果审稿人要求补充实验：
1. 列出所有被要求的实验
2. 评估每个实验的可行性和预计时间
3. 对于可行的实验，给出实验设计建议
4. 对于不可行的实验，起草合理的解释

## 模式 B：修改验证

当提供修改稿时，逐条检查审稿意见是否已被回应：

### Step 1：解析审稿意见（同模式 A）

### Step 2：解析修改稿

使用 Paper Parser MCP 或 Read 工具解析修改后的论文。
如提供了原始稿（`--original`），进行差异对比。

### Step 3：逐条验证

对每条 Weakness 和 Question：
1. 在修改稿中搜索对应的修改
2. 判断修改是否充分回应了审稿意见
3. 标注回应状态：

| 状态 | 说明 |
|------|------|
| ✅ 已充分回应 | 修改稿中有明确的、充分的修改 |
| ⚠️ 部分回应 | 有修改但不够充分 |
| ❌ 未回应 | 修改稿中找不到对应修改 |
| ℹ️ 无需修改 | 审稿人的小问题，不影响论文 |

### Step 4：输出验证报告

```markdown
# Revision Verification Report

## Overall Status
- Total issues: X
- Fully addressed: X (✅)
- Partially addressed: X (⚠️)
- Not addressed: X (❌)
- No action needed: X (ℹ️)

## Detailed Verification
### Reviewer #1
| Issue | Status | Evidence in Revised Paper |
|-------|--------|--------------------------|
| W1    | ✅     | Section 3.2, new Table 5 |
| W2    | ⚠️     | Modified but incomplete   |
| Q1    | ❌     | Not found                 |
```

保存为 `Revision_Check_[论文名].md`。
