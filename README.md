# 🎭 PersonaLab - A2A 产品验证沙盘

> 上线前的平行宇宙 —— 用 AI 模拟真实用户，在代码写下第一行之前验证产品逻辑

[![Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://github.com/lizuyi-6/personalab-demo)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 核心价值

**问题**：70% 的产品功能从未被使用，大量开发资源浪费在伪需求上

**方案**：用 A2A (Agent-to-Agent) 技术构建高逼真度用户模拟沙盘

- ✅ 在开发前验证产品假设
- ✅ 发现致命体验缺陷
- ✅ 预测留存率和 NPS
- ✅ 节省数月开发时间和数十万成本

---

## ✨ v0.3 新特性 - PRD 生成工作流

### 🎯 全新工作流

```
产品想法 → AI生成PRD → 用户确认 → 沙盘模拟 → 验证报告
```

**核心理念**：先让产品经理确认 AI 生成的 PRD 是否符合预期，再进行模拟。

| 功能 | 说明 |
|------|------|
| **🤖 PRD 自动生成** | 输入产品想法，AI 生成完整 PRD 文档 |
| **✏️ PRD 编辑确认** | 用户可以修改 PRD 后再模拟 |
| **📄 PRD 解析** | 上传 PRD 文档自动提取功能列表 |
| **📊 可视化图表** | 功能热度、行为分布图表 |
| **📥 报告导出** | 一键导出 Markdown 验证报告 |
| **🎭 真实性引擎** | 博弈论约束确保模拟真实性 |

---

## 🚀 快速开始

### 方式一：在线 Demo（推荐）

```bash
# 直接打开前端（内置 Demo 模式）
open frontend/index.html
```

无需后端即可体验完整流程！

### 方式二：完整部署

```bash
# 1. 克隆项目
git clone https://github.com/lizuyi-6/personalab-demo.git
cd personalab-demo

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 启动 API 服务
python api.py

# 4. 打开前端
open frontend/index.html
```

API 将在 `http://localhost:8000` 运行。

### 使用真实 LLM（可选）

```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY="sk-xxx"

# 启动服务
python api.py
```

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (index.html)                       │
│   需求输入 | PRD上传 | 结果可视化 | 图表 | 报告导出          │
├─────────────────────────────────────────────────────────────┤
│                    API (FastAPI)                            │
│   /simulate | /prd/parse | /report | /llm                  │
├─────────────────────────────────────────────────────────────┤
│                   核心引擎                                   │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │ Agent Generator │  │     Sandbox Engine              │   │
│  │ OCEAN 人格模型   │  │  真实性校验 | 博弈论约束         │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │   PRD Parser    │  │   Report Generator              │   │
│  │   文档解析       │  │   Markdown 报告生成             │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   LLM Router                                │
│   OpenAI GPT-4o | Claude | DeepSeek | Mock (离线)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 核心技术

### OCEAN 五因素人格模型

每个 AI Agent 都有独立的性格画像：

| 维度 | 含义 | 影响行为 |
|------|------|----------|
| **O**penness | 开放性 | 尝试新功能的意愿 |
| **C**onscientiousness | 尽责性 | 完成任务的坚持度 |
| **E**xtraversion | 外向性 | 社交分享倾向 |
| **A**greeableness | 宜人性 | 好评/投诉倾向 |
| **N**euroticism | 神经质 | 情绪波动/放弃率 |

### 真实性校验引擎

引入博弈论约束确保模拟真实：

- **注意力预算**：每个 Agent 每天只有有限的注意力
- **虚拟钱包**：购买行为需要消耗虚拟货币
- **疲劳机制**：重复操作增加疲劳，影响决策
- **情绪系统**：成功/失败影响后续行为

---

## 📊 使用示例

### 输入

```markdown
产品名称：效率笔记 App

核心功能：
- 核心笔记功能 | 复杂度: 0.3
- Markdown 编辑 | 复杂度: 0.5
- AI 智能摘要 | 复杂度: 0.7
- 团队协作 | 复杂度: 0.8

AI 用户数：50
虚拟天数：7
```

### 输出

```
📊 核心指标：
  - 注册转化率: 42%
  - 留存率: 38%
  - NPS: 15
  - 放弃率: 18%

💡 洞察建议：
  ⚠️ 留存率不足，用户缺乏持续使用的动力
  🔥 热门功能：核心笔记功能
  ❄️ 冷门功能：团队协作，考虑下线或优化

💬 AI 用户反馈：
  agent_23: "这个功能不错，解决了我的问题 👍"
  agent_45: "操作太复杂了，找不到入口 😕"
  ...
```

---

## 📁 项目结构

```
personalab-demo/
├── backend/
│   ├── api.py              # FastAPI 服务
│   ├── agent_generator.py  # Agent 生成器 (OCEAN)
│   ├── sandbox_engine.py   # 推演引擎
│   ├── llm_client.py       # LLM 路由器
│   ├── prd_parser.py       # PRD 解析器
│   ├── report_generator.py # 报告生成器
│   └── requirements.txt    # Python 依赖
├── frontend/
│   └── index.html          # Web 前端
└── README.md
```

---

## 🔌 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/agents/generate` | POST | 生成 AI 用户 |
| `/api/prd/parse` | POST | 解析 PRD 文档 |
| `/api/prd/upload` | POST | 上传 PRD 文件 |
| `/api/simulate` | POST | 运行沙盘模拟 |
| `/api/simulations/{id}` | GET | 获取模拟结果 |
| `/api/simulations/{id}/report` | GET | 导出完整报告 |
| `/api/llm/status` | GET | 查看LLM状态 |

---

## 🗺️ 路线图

### ✅ v0.2 (当前)
- [x] OCEAN 人格模型
- [x] 基础推演引擎
- [x] Web 前端 Demo
- [x] 核心指标计算
- [x] PRD 文档解析
- [x] 报告导出
- [x] 可视化图表

### 🚧 v0.3 (计划中)
- [ ] 接入真实 LLM 生成反馈
- [ ] Figma 原型集成
- [ ] A/B 测试对比
- [ ] 历史模拟管理

### 🎯 v1.0 (商业化)
- [ ] SaaS 平台
- [ ] 企业订阅系统
- [ ] 私有化部署
- [ ] API 开放平台

---

## 🤝 贡献

欢迎 Issue 和 PR！

---

## 📄 License

MIT License - 自由使用

---

## 🙏 致谢

灵感来源：
- [Moltbook](https://moltbook.com) - AI Agent 社区
- OCEAN 人格模型研究
- 博弈论与行为经济学

---

**Made with ❤️ by [Li Zuyi](https://github.com/lizuyi-6)**
