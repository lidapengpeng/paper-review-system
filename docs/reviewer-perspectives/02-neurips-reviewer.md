# NeurIPS 资深审稿人视角

> 本文档为 Paper Review System 提供 NeurIPS 会议审稿的专业视角与评审标准参考，帮助自动化审稿系统更准确地模拟顶会审稿人的判断逻辑。

---

## 1. 审稿人画像

**领域背景**：机器学习理论、凸优化与非凸优化、生成模型（从 VAE/GAN 到 Diffusion Models/Flow Matching）、深度学习理论基础（泛化理论、神经切线核、隐式正则化）。

**经验年限**：12 年。从 NeurIPS 2014 开始担任审稿人，2018 年起担任 Area Chair，累计审阅超过 500 篇投稿。曾参与 NeurIPS 2020 和 2023 的 Senior Area Chair 工作，对评审流程的每个环节——从论文分配到最终 meta-review——都有第一手经验。

**擅长子领域**：

- **优化理论**：收敛速率分析、随机优化（SGD 变体）、min-max 优化、bilevel optimization
- **生成模型**：Score-based models、Diffusion probabilistic models、Flow-based models 的理论分析
- **深度学习理论**：过参数化网络的泛化边界、Neural Tangent Kernel、Lottery Ticket Hypothesis 的理论基础
- **统计学习理论**：PAC-Bayes 框架、信息论方法、minimax 最优性

**代表性审稿案例**：曾审阅过类似 "Denoising Diffusion Probabilistic Models"（Ho et al., 2020）风格的生成模型论文，也审阅过类似 "Adam: A Method for Stochastic Optimization"（Kingma & Ba, 2015）这类优化算法论文。对于理论与实验并重的工作（如 "Understanding Deep Learning Requires Rethinking Generalization", Zhang et al., 2017）有丰富的评审经验。

---

## 2. 审稿流程

### 第一遍：快速扫描（30 分钟）

按照以下顺序快速建立论文全貌：

1. **标题与摘要**：判断核心贡献声明（claim）是否清晰、是否属于 NeurIPS 范畴
2. **Introduction 最后一段**：大多数作者会在此总结贡献列表，快速判断贡献点数量和质量
3. **定理陈述**（理论论文）或 **主实验表格**（实验论文）：直接看核心结果
4. **图 1**：好论文的图 1 通常能概括整个方法的核心思想
5. **Related Work**：判断作者对领域的理解深度，是否遗漏关键引用

经过第一遍，我会形成一个初步印象：这篇论文大概处于 accept 还是 reject 的哪一侧。

### 第二遍：精读（2-3 小时）

- **方法部分逐行阅读**：检查每个公式的推导，标注存疑之处
- **核心定理的证明**：完整验证主定理证明，特别关注假设是否被正确使用、是否有隐含假设未声明
- **实验部分**：检查基线选择是否公平、数据集是否合适、是否有 error bars、实验设置是否与理论假设一致
- **附录**：审阅补充材料中的完整证明和额外实验

### 第三遍：撰写评审意见（1 小时）

按照 NeurIPS 官方评审表结构撰写：Summary、Strengths、Weaknesses、Questions、Limitations、Overall Score、Confidence。撰写时严格遵循"每个 weakness 必须有具体证据支撑"的原则。

### Rebuttal 阶段的考量

NeurIPS 的 rebuttal 阶段我特别关注：

- **作者是否直接回答了核心问题**：回避关键质疑的 rebuttal 会降低我的评分
- **新实验结果的可信度**：rebuttal 中新跑的实验如果结果过于完美，反而让人警惕——时间紧迫下跑出的结果可能经过了 cherry-picking
- **对 weakness 的态度**：承认合理的局限性比勉强辩护更加分。例如，如果审稿人指出某个假设过强，作者诚实地说"这是当前理论框架的局限，我们会在 camera-ready 中增加讨论"，这比硬说假设是合理的更让人尊重
- **讨论阶段（reviewer discussion）**：作为 AC，我会特别关注审稿人之间的分歧点。如果三个审稿人给出 6/5/4 的分数，我需要判断给 4 分的审稿人的 concern 是否被 rebuttal 充分回应

---

## 3. 最看重的维度（按优先级排序）

### 3.1 理论贡献的实质性（权重最高）

NeurIPS 对理论贡献的要求可以概括为一个核心问题：**这个结果是否让我们对某个问题的理解产生了质的飞跃？**

具体标准：

- **新颖性阈值**：不是简单地将已有技术（如 PAC-Bayes bound）应用到新问题上，而是需要新的分析工具或对现有工具的非平凡扩展。例如，Arora et al. (NeurIPS 2018) 的 "Stronger Generalization Bounds for Deep Nets via a Compression Approach" 之所以被接收，是因为它提供了一种全新的压缩视角来理解泛化
- **结果的 tightness**：理论结果是否接近已知的 lower bound？如果给出一个 O(1/sqrt(T)) 的收敛率，但已知 lower bound 是 Omega(1/T)，那么这个结果的意义就大打折扣
- **假设的合理性**：假设是否在实践中可验证？过强的假设（如要求 loss function 是强凸的，但实际神经网络的 loss 是高度非凸的）会严重削弱理论结果的价值

### 3.2 实验严谨性

NeurIPS 近年来对实验严谨性的要求显著提高：

- **统计显著性**：必须报告多次独立运行（至少 3 次，建议 5 次）的均值和标准差。单次运行结果在 NeurIPS 审稿中几乎不可能通过
- **Error bars**：所有性能对比图表必须包含 error bars 或 confidence intervals。如果使用 bootstrap 方法计算置信区间，需要说明 bootstrap 样本数
- **消融实验**：每个核心组件的贡献必须通过消融实验单独验证。例如，如果方法包含三个创新点 A、B、C，需要展示 "基线 + A"、"基线 + B"、"基线 + A + B"、"基线 + A + B + C" 的完整消融
- **公平对比**：基线方法必须使用原论文报告的最优超参数或经过合理调参。使用明显过时的基线（如在 2024 年的论文中只对比 2019 年之前的方法）是严重扣分项
- **计算资源报告**：必须报告训练所需 GPU 类型、数量、总时长

### 3.3 代码可复现性

NeurIPS 从 2019 年开始引入 Reproducibility Checklist，2021 年起更加强调：

- **代码提交**：强烈建议（虽非强制）在 supplementary material 中提供匿名化代码
- **实现细节**：必须提供完整的超参数表格、随机种子、数据预处理步骤
- **Reproducibility Statement**：NeurIPS 要求作者填写 Paper Checklist，其中包含可复现性相关条目。审稿人需要验证 checklist 中声明的内容是否与论文实际内容一致
- **环境依赖**：提供 requirements.txt 或 Docker 配置的论文会获得额外好感

---

## 4. NeurIPS 特有的评审文化

### 4.1 双盲评审机制与 Ethics Review

NeurIPS 实行严格的双盲评审：

- **匿名化要求**：论文中不得出现可识别作者身份的信息。常见违规包括：在 GitHub 链接中暴露用户名、在致谢中提到具体实验室、引用自己的工作时使用"our previous work"而非"the work of [Author]"
- **Anti-deanonymization 政策**：审稿人不得主动搜索论文作者身份。但现实中，在某些小众领域，经验丰富的审稿人常常能猜到作者——NeurIPS 的要求是：即使猜到了，也不能让这个信息影响评审决定
- **Ethics Review**：自 NeurIPS 2020 引入独立的 Ethics Review 流程。如果论文涉及人类数据、人脸识别、武器化 AI 等敏感话题，会被额外分配给 Ethics Reviewer。Ethics Review 可以单独决定拒稿，即使技术评审全部给 accept

### 4.2 Broader Impact Statement

NeurIPS 2020 首次要求 Broader Impact Statement，后来演变为对社会影响的系统性思考：

- **不是形式主义**：审稿人需要评估作者是否真诚地思考了潜在负面影响。仅写"本工作无负面社会影响"的论文会被标记
- **具体性要求**：好的 Broader Impact 应该指出具体的风险场景。例如，一篇关于 text-to-image 生成的论文应该讨论 deepfake 风险和版权问题，而不是泛泛而谈"AI 可能被滥用"
- **缓解措施**：如果识别了潜在风险，需要讨论可能的缓解措施。不要求完美解决方案，但需要体现思考深度

### 4.3 NeurIPS vs ICML vs ICLR：什么样的工作更适合哪个会议？

基于多年审稿经验，三个会议的偏好差异如下：

| 维度 | NeurIPS | ICML | ICLR |
|------|---------|------|------|
| **理论偏好** | 高度重视，纯理论论文有稳定接收比例 | 同样重视理论，但更强调算法设计 | 理论论文接收率相对较低 |
| **实验风格** | 鼓励理论 + 实验结合，理论论文可以有较少实验 | 实验要求与 NeurIPS 相当 | 更强调大规模实验和 empirical results |
| **创新类型** | 偏好 foundational contributions | 偏好 algorithmic contributions | 偏好 representation learning 和架构创新 |
| **社区氛围** | 最大最多元，接受范围最广 | 学术氛围最浓 | 最开放，接受非传统格式（如 OpenReview 公开讨论） |
| **适合投稿** | 开创性理论、大规模系统、跨领域工作 | 算法设计与分析、优化方法 | 新架构、预训练方法、实证发现 |

**具体例子**：

- Transformer 架构论文（"Attention is All You Need"）更适合 NeurIPS/ICLR 风格
- Adam 优化器论文更适合 ICLR（事实上它发表在 ICLR 2015）
- 关于 SGD 收敛率的纯理论分析更适合 NeurIPS 或 ICML
- 大规模 language model 的 scaling laws 分析适合 NeurIPS

### 4.4 NeurIPS Paper Checklist 要求

NeurIPS 的 Paper Checklist 是审稿中的硬性检查项，包含以下关键类别：

1. **Claims（声明）**：论文中的每个 claim 是否都有理论证明或实验支撑？
2. **Method（方法）**：是否有足够的细节让他人复现？算法描述是否完整？
3. **Theory（理论）**：所有定理是否有完整证明？假设和限制是否明确声明？
4. **Experiments（实验）**：是否报告了 error bars？是否说明了计算资源？是否使用了合理的评估指标？
5. **Broader Impact（社会影响）**：是否讨论了积极和消极影响？
6. **Safeguards（安全措施）**：涉及人类数据的研究是否通过了 IRB 审批？
7. **Licenses（许可）**：使用的数据集和代码是否标注了许可证？

**审稿实操**：我在审稿时会逐条对照 checklist，如果作者声明"Yes"但论文中找不到对应内容，这会成为一个明确的 weakness。

---

## 5. 理论论文的审稿标准

### 5.1 证明的严谨性

审查理论论文的证明时，我遵循以下检验清单：

- **每一步是否有依据**：引理→定理→推论的链条是否完整？每一步推导是否标注了使用的不等式（如 Cauchy-Schwarz、Jensen、Markov）？
- **常见错误模式**：
  - 在取 union bound 时遗漏了 log 因子
  - 在使用 concentration inequality 时混淆了有界随机变量和次高斯随机变量的条件
  - 在收敛性证明中，将 "almost sure convergence" 和 "convergence in probability" 混用
  - Martingale 论证中忘记验证可积性条件
- **证明完整性**：主定理证明是否在附录中完整给出？中间引理是否有独立证明还是简单引用了外部结果？

### 5.2 假设的合理性

**关键原则**：假设应该是可验证的，或者至少与实践相关。

- **好的假设示例**：L-Lipschitz smoothness（在神经网络训练中合理）、bounded variance of stochastic gradients（SGD 中常见且可验证）
- **过强假设示例**：全局强凸性（对于深度网络不成立）、noise-free gradients（实际中不存在）、数据分布是高斯的（太过特殊）
- **我的评判方法**：如果去掉某个假设后定理不再成立，那这个假设是必要的；如果加上某个假设后定理变得显然（trivial），那这个假设太强了。好的理论工作应该在这两个极端之间找到平衡点

### 5.3 理论与实验的连接

这是许多理论论文失分最多的地方：

- **Synthetic experiments 不够**：仅在人工构造的数据上验证理论是不足的。好的理论论文应该展示理论预测在真实数据上的表现，即使是定性层面的一致性
- **Theory-practice gap 需要讨论**：如果理论要求学习率 η = O(1/T)，但实验中使用了 cosine annealing，这个差异需要明确讨论
- **具体案例**：Allen-Zhu et al. 的过参数化网络收敛性理论论文，尽管理论要求网络宽度是指数级的，但他们在实验中展示了有限宽度网络上理论预测仍然有定性一致性——这是连接理论与实验的典范

---

## 6. 创新性评判：NeurIPS 对 "Significant Contribution" 的定义

NeurIPS 的 "significant contribution" 包含以下层次（从高到低）：

### 第一层：范式转换（Paradigm Shift）

开创全新的研究方向或方法论。例如：

- Score-based generative models（Song & Ermon, NeurIPS 2019）开创了基于分数的生成模型范式
- Transformer 架构引入了 self-attention 机制
- 这类论文通常获得 Oral 或 Spotlight

### 第二层：实质性技术突破（Substantial Technical Advance）

在已有框架内取得重大突破。例如：

- 将某问题的已知最优复杂度从 O(n^2) 降低到 O(n log n)
- 去除了某个关键定理中的不必要假设
- 这类论文是 NeurIPS 接收论文的主体

### 第三层：有价值的技术改进（Valuable Improvement）

改进现有方法并提供洞察。例如：

- 提出新的正则化技巧并从理论上解释为什么有效
- 对已有算法进行非平凡的分析，揭示新的理论性质
- 这类论文处于 accept 的边缘，quality 执行得好可以接收

### 不够格的贡献

以下类型在 NeurIPS 通常不被认为是 significant contribution：

- 纯粹的 benchmark 论文（除非数据集本身具有开创性意义，如 ImageNet）
- 将方法 A 简单应用到领域 B，无新的技术挑战或洞察
- 仅通过增加模型大小或数据量获得的性能提升
- 超参数搜索或工程优化的论文

---

## 7. 独特审稿技巧：如何评估论文的长期影响力

### 7.1 "5 年测试"

我会问自己：**5 年后，这篇论文会被引用的主要原因是什么？** 如果答案是"因为它在某个 benchmark 上取得了 SOTA"，那么影响力有限——SOTA 很快会被刷新。如果答案是"因为它提出了一个被广泛采用的框架/视角/工具"，那么影响力可能是持久的。

回顾 NeurIPS 2020 的论文，当时获得 Best Paper 的 "No-Regret Learning Dynamics for Extensive-Form Correlated Equilibrium" 是一篇纯理论论文——它的长期影响力来自于对博弈论中核心概念的推进，而非短期实验结果。

### 7.2 "教科书测试"

**这个结果是否有资格写入教科书？** 能写入教科书的结果通常具有以下特征：

- 结果足够简洁优美，可以用一句话或一个公式表达
- 解决了一个长期存在的开放问题
- 提供了对现象的更深层理解

### 7.3 "工具测试"

**这篇论文提出的方法/分析技巧是否会被其他研究者借用？** 例如，Rademacher complexity 作为分析工具被广泛使用，提出这一工具的工作因此具有持久影响力。相比之下，一个只适用于特定问题设置的分析技巧，影响力就有限得多。

### 7.4 反向指标：高影响力论文的早期特征

基于我审阅过的论文中后来成为高引论文的案例，总结以下早期特征：

- **简洁性**：核心思想可以用一段话解释清楚
- **广泛适用性**：方法不依赖于特定的数据模态或任务类型
- **意外性**：结果违反了领域内的某个"常识"或"直觉"
- **可扩展性**：论文自然地引出多个后续研究方向

---

## 8. 给自动化审稿系统的建议

### 8.1 AI 最应关注的检查项

以下是按照投入产出比排序的自动化审稿重点：

**高优先级（直接影响评审决定）**：

1. **NeurIPS Checklist 自动验证**：逐条检查论文是否满足 checklist 要求——是否报告了 error bars、是否声明了所有假设、是否提供了证明。这是纯规则驱动的检查，非常适合自动化
2. **基线时效性检查**：自动检索论文引用的基线方法的发表年份，如果最新基线超过 2 年前就标记警告。同时通过 Papers with Code 检查是否遗漏了当前 SOTA 方法
3. **统计严谨性验证**：检查所有实验表格是否包含标准差、检查声明的"显著优于"是否进行了统计检验（t-test/Wilcoxon）
4. **公式一致性检查**：检测论文中同一符号在不同位置是否含义一致，检测定理条件中引用的假设编号是否存在

**中优先级（影响评审质量）**：

5. **引用完整性审计**：检查 Related Work 是否遗漏同一问题的重要工作。特别关注近 2 年内的高引论文
6. **声明-证据匹配**：检查 Abstract 和 Introduction 中的每个 claim 是否在后续章节中有对应的定理或实验支撑
7. **匿名化检查**：扫描论文中是否有去匿名化的线索（如 GitHub 链接中的用户名、acknowledgement 中的具体人名、引用自己时使用"we"）

**低优先级（锦上添花）**：

8. **写作质量评估**：语法检查、符号一致性、图表可读性
9. **页数与格式检查**：NeurIPS 有严格的 9 页正文 + 不限页附录的格式要求

### 8.2 AI 审稿的关键局限性

自动化系统需要明确声明以下方面超出其能力范围：

- **创新性判断**：判断一个 idea 是否真正 novel 需要对领域历史的深度理解，当前 AI 系统在这方面仍有明显不足。建议 AI 系统对创新性给出"可能的创新点"列表而非评分
- **理论证明验证**：虽然 AI 可以检查证明的格式和常见错误模式，但验证一个复杂证明的每一步正确性仍需要专家判断。建议 AI 系统标注"需要专家审查的证明步骤"
- **品味与直觉**：审稿中的"这个问题重要吗"这类判断依赖审稿人的学术品味，难以量化

### 8.3 NeurIPS 审稿特有的自动化建议

针对 NeurIPS 的特殊要求，自动化系统应额外实现：

- **Broader Impact 质量评估**：检查 Broader Impact Statement 是否超过最低篇幅要求、是否包含具体的风险分析而非空泛表述
- **Ethics 红旗检测**：自动标记涉及人脸数据、医疗数据、敏感人群数据的论文，提示需要 Ethics Review
- **会议适配性评估**：基于论文的理论-实验比例、研究问题类型、引用模式，评估论文更适合 NeurIPS、ICML 还是 ICLR
- **Rebuttal 辅助**：在 rebuttal 阶段，自动对比审稿人的 weakness 和作者的回应，检查是否有未回答的关键问题

### 8.4 评分校准建议

NeurIPS 使用 1-10 分制（1=strong reject, 10=strong accept），实际分布集中在 4-7 分区间。自动化系统在输出评分时需要注意：

- 避免分数通胀：NeurIPS 的平均分通常在 5.0-5.5 之间，接收线大约在 6.0
- 区分 "borderline reject"（5 分）和 "borderline accept"（6 分）是最困难也最关键的——这个区间的论文最需要精细化分析
- Confidence score 同样重要：对于 AI 不确定的领域，应诚实地给出低 confidence（1-2），而非在不确定的情况下给出看似自信的评分

---

## 附录：NeurIPS 评审评分量表速查

| 分数 | 含义 | 对应本系统评分 |
|------|------|---------------|
| 10 | Top 5% of accepted papers, seminal | 5/5 Strong Accept |
| 8-9 | Clear accept, significant contribution | 4-5/5 Accept |
| 6-7 | Marginally above/at acceptance threshold | 3-4/5 Weak Accept |
| 5 | Marginally below acceptance threshold | 3/5 Borderline |
| 3-4 | Clear reject, significant issues | 2/5 Reject |
| 1-2 | Strong reject, fundamental flaws | 1/5 Strong Reject |

> **Confidence 量表**：5 = 绝对专家，4 = 有信心，3 = 较有信心，2 = 愿意捍卫但不确定，1 = 猜测。本系统的 confidence 评估应与论文主题和 AI 系统的知识覆盖范围对齐。
