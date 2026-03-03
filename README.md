# Paper Review System

学术论文自动化审稿系统 - Claude Code 插件。

集成 PDF 解析、参考文献验证、SOTA 对比、代码审查，覆盖 8 个评审维度，输出专业的结构化评审报告。

## 功能特点

- **PDF 智能解析**：全文 Markdown 转换 + LaTeX 公式恢复 + 图表裁剪为 PNG
- **参考文献审计**：通过 CrossRef + DBLP + Semantic Scholar 自动验证每条参考文献
- **SOTA 对比**：自动获取排行榜数据和竞争方法，对比论文实验结果
- **遗漏引用检测**：发现应该引用但未引用的重要论文
- **8 维度评审**：摘要与动机、新颖性、技术正确性、实验、写作质量、可复现性、相关工作、补充材料
- **代码审查**：可选的论文-代码一致性检查
- **并行评审**：5 个 Agent 并行处理，大幅提高审稿效率

## 快速开始

```bash
# 安装插件后，在 Claude Code 中使用：

# 审阅论文
/paper-review-system:review-paper /path/to/paper.pdf

# 论文 + 代码审查
/paper-review-system:review-paper /path/to/paper.pdf --with-code /path/to/code/

# 论文 + 代码 + 补充材料
/paper-review-system:review-paper /path/to/paper.pdf --with-code ./code/ --with-supplement ./supplement.pdf
```

## 审稿流程

| 阶段 | 内容 | 说明 |
|------|------|------|
| **Phase 1** | PDF 解析 | 全文 Markdown + 参考文献 + 图表提取 |
| **Phase 2** | 8 维度并行评审 | 5 个 Agent 同时工作 |
| **Phase 3** | 代码审查（可选） | 论文-代码一致性检查 |
| **Phase 4** | 报告生成 | 结构化评审报告 + 评分 + 接收建议 |

## 插件组件

| 组件 | 类型 | 功能 |
|------|------|------|
| `paper-review` | Skill | 审稿方法论 + 评分标准 |
| `/review-paper` | Command | 用户入口，接收 PDF 路径 |
| `paper-analyzer` | Agent | PDF 解析和结构分析 |
| `technical-reviewer` | Agent | 公式验证 + 实验分析 + SOTA 对比 |
| `reference-auditor` | Agent | 参考文献审计 + 遗漏引用检测 |
| `paper-parser` | MCP Server | PDF → Markdown + 图表提取 |
| `academic-search` | MCP Server | 参考文献验证 + 学术搜索 |

## 前置条件

### Python 依赖

```bash
# Paper Parser MCP
pip install mcp marker-pdf pymupdf4llm pydantic Pillow

# Academic Search MCP
pip install mcp httpx pydantic
```

### 可选配置

设置 Semantic Scholar API Key 可将参考文献验证速度从 ~40s 提升至 ~3-5s：

```bash
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"
export CROSSREF_MAILTO="your-email@example.com"
```

## 输出

评审报告保存在 PDF 同目录下：`Review_Report_[论文名].md`

包含：
- 论文摘要总结
- 优点 / 缺点
- 参考文献审计（验证结果 + 遗漏引用）
- SOTA 对比（排行榜 + 竞争方法）
- 8 维度详细评分（1-5 分）
- 代码审查结果（如适用）
- 给作者的问题
- 接收建议（Strong Accept → Strong Reject）

## 安装

### 本地测试

```bash
claude --plugin-dir /path/to/paper-review-system
```

### 从市场安装

```bash
/plugin install paper-review-system@marketplace-name
```

## License

MIT
