# DUT Link — Claude Code 开发主 Prompt

> 使用说明：把本文件复制为项目根目录的 `CLAUDE.md`，让 Claude Code 在每次会话中都能读到项目全貌。开发时按"阶段化 prompt"方式逐步喂给 Claude Code（你之前深渊回响项目用过的工作流），不要一次性要求它把整个项目写完。

---

## 0. 项目一句话定位

DUT Link 是一个 AI 驱动的校园连接平台：通过分析用户的技能/经历/兴趣，生成能力画像，并反过来推荐"用户不会主动搜索但有价值"的机会、队友和跨领域知识连接。核心差异化不是"推荐你喜欢的"，而是"发现你没想到的"。

黑客松目标：2-3人团队、时间较宽松、Web端Demo。目标是做出**能跑通完整AI流程、有真实种子数据支撑、可现场演示的产品**，而不是纯UI原型。

---

## 1. 技术选型（含理由）

| 层 | 选型 | 理由 |
|---|---|---|
| 后端 | FastAPI + Python 3.11+ + Pydantic v2 | 你已有FastAPI/LangChain经验，上手快，异步性能够用 |
| AI编排 | LangGraph | 三个功能天然是三个可组合的Agent（画像/匹配/探索），LangGraph比裸调用API更适合展示"AI工作流"这个卖点 |
| LLM | DeepSeek API（你已有cc-switch环境）或 Claude API 二选一，建议**画像生成/匹配用DeepSeek省成本，知识盲盒探索用Claude效果更好** | 控制成本+发挥各自强项 |
| 数据库 | PostgreSQL + pgvector（如部署麻烦则退化为 SQLite + numpy 手算余弦相似度） | 技能画像需要向量化做相似度匹配 |
| 前端 | React + Vite + TypeScript + TailwindCSS + shadcn/ui | 现代、组件库齐全，demo视觉效果好 |
| 数据可视化 | Recharts（雷达图展示技能画像）+ react-force-graph 或 D3（校园连接网络图，**建议加，很加分**） | README里"技术能力雷达图"和"连接网络"都是天然的可视化点 |
| 部署 | Docker Compose 一键起 backend + frontend + db | 现场演示零故障率 |

---

## 2. 团队分工建议（2-3人）

- **A - 后端负责人**：FastAPI路由、数据库模型、鉴权、种子数据脚本
- **B - AI负责人**：LangGraph三个Agent的pipeline与prompt调优、向量化与匹配算法
- **C - 前端负责人**：画像可视化、组队推荐UI、知识盲盒卡片流、连接网络图

如果是2人：A+B合并（一人管后端+AI），C单独管前端；两人都要参与prompt调优。

---

## 3. 数据模型（先定这个，别让Claude Code自由发挥）

```
User
  id, name, major, grade, bio_raw(用户自述文本)
  github_url, portfolio_urls[]

SkillProfile (由AI生成，与User一对一)
  user_id
  skill_vector: dict[str, float]   # 如 {"后端开发":0.8, "游戏开发":0.7, "算法基础":0.6}
  interest_tags: list[str]
  potential_directions: list[str]  # AI推测的"潜在方向"
  embedding: vector(N)             # 用于pgvector相似度检索
  raw_llm_output: json             # 保留AI原始分析，便于可解释性展示

Team
  id, name, goal_description
  member_ids: list[user_id]

TeamGapAnalysis (AI生成)
  team_id
  existing_strengths: list[str]
  missing_skills: list[str]        # AI判断的能力缺口

Match (团队推荐结果)
  team_id, candidate_user_id
  match_score: float
  match_reasons: list[str]         # 必须结构化输出，不能只给分数

DiscoveryCard (知识盲盒)
  id, target_user_id
  content_title, content_reason    # "为什么推荐这个"的逻辑链条
  suggested_connection_user_id     # 推荐去认识的人（可为空）
  connection_reason

Connection (用户间产生的连接记录，用于最终的"校园连接网络图")
  user_a_id, user_b_id, source_type  # source_type: team_match / discovery
```

---

## 4. 三个 AI Agent 的 Prompt 设计规范

这是整个项目的核心，Claude Code写代码时**必须**严格按以下结构设计system prompt，防止输出空泛或牵强。

### Agent 1：技能画像生成 Agent
- 输入：用户自述、项目经历列表、GitHub仓库描述（可选调用GitHub API抓取repo语言/README）
- **强制要求结构化JSON输出**：`skill_vector`（5-8个维度，0-1打分）、`interest_tags`（3-6个）、`potential_directions`（2-3个，且每个方向必须附一句"推理依据"，不能凭空给方向）
- Prompt要点：明确告诉LLM"不要只总结用户说了什么，要推理用户可能适合但没提到的方向，并给出具体依据"

### Agent 2：智能组队匹配 Agent
- 输入：团队现有成员的skill_vector集合、候选人池的skill_vector
- 处理分两步（不要让LLM直接算分数，先用向量相似度做候选人召回，再用LLM做可解释性打分）：
  1. 代码层：计算团队能力空缺 = 目标能力集合 - 现有能力覆盖，用向量距离筛出Top 10候选人
  2. LLM层：对Top 10逐一生成 `match_score` + **结构化match_reasons**（至少2条具体证据，如"有前端项目经历"、"作品集中有UI设计案例"）
- 防止空泛输出：prompt里要求"每条理由必须引用候选人画像中的具体字段，不能说套话"

### Agent 3：知识盲盒探索 Agent（最容易翻车的部分，重点约束）
- 输入：目标用户的skill_vector + interest_tags
- **必须两步生成，且第二步要做逻辑校验**：
  1. 生成一个跨领域知识主题 + **具体的类比依据**（如"模块化架构 vs 建筑空间设计"，依据要说清楚"相似点具体是什么"）
  2. 从用户池中找一个专业/兴趣互补的人，理由必须包含"可能的具体讨论话题"（不能只说"你们都感兴趣XX"）
- Prompt要点：**明确禁止AI输出过于宽泛的类比**（如"编程和音乐都需要创造力"这种放之四海皆准的废话），要求给出至少一个具体的、可操作的连接点

---

## 5. 开发任务拆解（对应README的Phase 1-3，可并行）

### Phase 1：基础平台（第一优先级，必须完成）
- [ ] 后端：User CRUD API、bio_raw录入接口
- [ ] AI：Agent 1 画像生成 pipeline 打通，输出结构化JSON并入库
- [ ] 前端：用户信息录入表单 + 技能雷达图展示页
- [ ] **种子数据脚本**：手写15-20个虚构但真实感强的学生画像（覆盖不同专业：软工/建筑/数媒/设计等），跑一遍Agent 1生成对应SkillProfile并存库——这是保证demo效果的关键，现场不能只有1-2个真实用户

### Phase 2：智能连接
- [ ] 后端：Team CRUD、候选人向量召回逻辑
- [ ] AI：Agent 2 匹配pipeline，输出match_score+match_reasons
- [ ] 前端：团队能力缺口可视化 + 推荐候选人卡片（展示具体匹配理由）

### Phase 3：探索系统
- [ ] AI：Agent 3 知识盲盒pipeline
- [ ] 前端：知识盲盒卡片流（类似"今日探索"信息流）
- [ ] **加分项**：Connection记录聚合，用react-force-graph画出"校园连接网络图"，demo收尾展示全局效果，视觉冲击力强

---

## 6. Claude Code 使用建议

- **善用你已有的 context7 MCP**：写LangGraph pipeline前先让Claude Code用context7查一下LangGraph最新API（尤其StateGraph、条件边写法，版本迭代快容易用旧写法）；写pgvector集成时同理查一下SQLAlchemy+pgvector的最新用法
- **分阶段喂prompt**，建议顺序：
  1. 先让它搭好项目骨架（FastAPI目录结构+React骨架+docker-compose），不要带业务逻辑
  2. 单独一轮实现数据模型和迁移
  3. 单独一轮实现Agent 1，跑通后再做Agent 2、3（三个Agent不要一次性要求全写，容易互相污染逻辑）
  4. 种子数据脚本单独一轮，确保有demo数据后再做前端联调
  5. 前端页面逐个来，别一次要求做完整个UI
- 建议在CLAUDE.md里固定写死本文档的"数据模型"和"Agent Prompt设计规范"两节，防止Claude Code在多轮对话中把字段名或输出格式改飘

---

## 7. 现场Demo脚本建议（对应README Demo展示流程）

1. 开场：展示已有的~15个种子用户画像雷达图，快速建立"这不是空壳"的印象
2. 现场录入一个新用户（可以是评委即兴报的经历），实时生成画像——这是"AI真的在跑"的关键证明环节
3. 展示团队组队推荐：预设一个"缺UI设计"的团队，展示推荐候选人+具体理由
4. 知识盲盒：展示1-2个跨领域连接案例，重点讲清楚"为什么这个连接有意义"而不只是"AI说了算"
5. 收尾：展示连接网络图，讲"这就是我们想让校园变成的样子"

---

## 8. MVP边界（时间宽松也要设边界，防止团队3人各自发散）

**必须做**：Phase 1 全部 + Phase 2 全部 + 种子数据
**尽量做**：Phase 3 知识盲盒pipeline + 卡片UI
**如果时间允许再做**：连接网络图可视化、GitHub仓库自动抓取分析、用户鉴权登录系统（demo阶段可以先跳过登录，用固定演示账号）
