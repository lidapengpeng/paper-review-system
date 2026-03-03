# 端到端测试反馈 — 2026-03-04

## 测试论文
- **Title**: Leveraging Fine-Grained Information and Noise Decoupling for Remote Sensing Change Detection
- **Venue**: ICME 2025
- **Domain**: Remote Sensing Change Detection

## 发现的问题

### P0 - 严重问题

#### 1. MCP Server 路径问题
`.mcp.json` 中使用 `${CLAUDE_PLUGIN_ROOT}`，但当用 `--plugin-dir` 测试时，需要确认该环境变量是否正确解析。实际测试中 MCP server 未启动（需要先 pip install 依赖）。

**影响**：整个 Phase 1 的自动解析无法工作。
**解决**：README 中需要更突出依赖安装步骤；考虑添加安装检查脚本。

#### 2. venue-profiles.md 不包含 ICME
当前只覆盖 10 个顶会（CVPR/NeurIPS/ICML/ICLR/ECCV/ICCV/ACL/AAAI/KDD/MICCAI），但用户投稿的 ICME 不在列表中。

**影响**：`--venue ICME` 无法加载对应策略。
**解决**：增加更多会议（ICME, WACV, BMVC, IJCAI, MM 等），或提供「自定义 venue」能力。

#### 3. 竞品论文检索能力不足
审稿中最重要的环节之一是「这篇论文对比的基线是否足够新」。当前系统仅通过 `find_competing_methods` 搜索，但：
- 没有明确的时间窗口限制（如最近 12 个月）
- 没有按任务+数据集精确匹配的能力
- 缺少从论文中自动提取 task/dataset 的逻辑

### P1 - 重要问题

#### 4. Phase 1.5 速读缺少自动化
速读评估（图表密度、引用时效性、结构完整性）目前是文字描述，没有实际的自动化检查脚本。

#### 5. 统计严谨性检查缺少自动化
"是否有 error bars" 这类检查可以通过扫描表格中的 ± 符号自动判断，但当前没有实现。

#### 6. 报告模板中缺少「竞品论文对比」独立章节
当前 SOTA Comparison 章节仅展示排行榜，缺少与最相近竞品论文的技术路线深度对比。

### P2 - 改进建议

#### 7. 应支持直接读取 PDF 进行视觉分析
Claude 本身可以直接读取 PDF 图像。当 MCP Server 不可用时，应有 fallback 方案。

#### 8. 评审报告增加「领域特异性检查」
遥感论文有特殊的评审关注点（如空间分辨率、传感器类型、多时相配准），当前系统不了解这些。
