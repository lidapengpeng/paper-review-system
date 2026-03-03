---
name: pre-screen
description: 论文快速质量预筛选，不做完整审稿，仅输出量化质量信号。适合批量筛选。
argument-hint: "<pdf_path> [--venue <conference>]"
allowed-tools:
  - Read
  - Bash
  - Grep
  - AskUserQuestion
  - mcp__paper-parser__*
---

# 论文快速预筛选

在不做完整审稿的情况下，快速评估论文的基础质量信号。适合：
- 批量筛选多篇待审论文，决定优先审哪篇
- 投稿前自查论文是否符合目标会议要求
- 快速判断论文的质量水位

## 流程

### Step 1：解析论文文本

优先使用 MCP，fallback 直接读取 PDF：
1. 调用 `paper_parser.parse_paper` 或用 Read 工具读取 PDF
2. 将解析文本保存到临时文件

### Step 2：运行自动化速读脚本

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/quick-assess.py <text_file>
```

### Step 3：输出格式化报告

将 JSON 结果转为可读格式：

```markdown
# 论文预筛选报告

**论文**: [标题]
**目标会议**: [venue]
**预筛选时间**: [日期]

## 质量信号

| 指标 | 结果 | 状态 |
|------|------|------|
| 论文类型 | 实验型 | - |
| 引用时效性 | 近 2 年占比 25% | ✅ 良好 |
| 结构完整性 | 78% (缺 Limitations) | ⚠️ 基本完整 |
| 匿名化合规 | 无问题 | ✅ 合规 |
| 统计严谨性 | 有 error bars | ✅ 有 |
| 效率指标 | 报告了 FLOPs 和 FPS | ✅ 有 |

## 质量信号汇总
- ✅ × N
- ⚠️ × N

## 初步评估
[1-2 句话的质量水位判断]

## 建议
[如果做完整审稿，应重点关注什么]
```

### Step 4：会议适配检查（如指定 venue）

如果指定了 `--venue`，额外检查：
- 该会议的强制 Checklist 是否满足
- 格式要求是否符合（页数限制等）
- 是否有该会议特别看重但论文缺失的内容

保存报告为 `PreScreen_[论文名].md`。

## 注意事项

- 此命令仅做表面质量检查，**不评估内容质量**（不做公式验证、不做 SOTA 对比）
- 执行时间：< 1 分钟
- 适合作为完整 `/review-paper` 的前置步骤
