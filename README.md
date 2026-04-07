# 🎭 PersonaLab - A2A 产品验证沙盘

> 上线前的平行宇宙 —— 用 AI 模拟真实用户，在代码写下第一行之前验证产品逻辑

[![Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://personalab-demo.vercel.app)
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

## 🚀 快速开始

### 方式一：在线 Demo

```bash
# 打开前端页面
open frontend/index.html
```

前端内置了 Demo 模式，无需后端即可体验完整流程。

### 方式二：完整部署

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 启动 API 服务
python api.py

# 3. 打开前端
open frontend/index.html
```

API 将在 `http://localhost:8000` 运行。

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (index.html)                       │
│   需求输入 | 结果可视化 | 实时反馈流                           │
├─────────────────────────────────────────────────────────────┤
│                    API (FastAPI)                            │
│   POST /api/simulate | GET /api/simulations/:id            │
├─────────────────────────────────────────────────────────────┤
│                   核心引擎                                   │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │ Agent Generator │  │     Sandbox Engine              │   │
│  │ OCEAN 人格模型   │  │  真实性校验 | 博弈论约束         │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
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

## 📊 Demo 效果

输入：
```
产品名称：效率笔记 App
功能列表：
  - 核心笔记功能 | 复杂度: 0.3
  - Markdown 编辑 | 复杂度: 0.5
  - AI 智能摘要 | 复杂度: 0.7
  - 团队协作 | 复杂度: 0.8

AI 用户数：50
虚拟天数：7
```

输出：
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
  agent_12: "AI 摘要有时候不准，不如自己写"
  ...
```

---

## 🗺️ 路线图

### Phase 1 (当前) - MVP Demo
- [x] OCEAN 人格模型
- [x] 基础推演引擎
- [x] Web 前端 Demo
- [x] 核心指标计算

### Phase 2 - 增强版本
- [ ] 接入真实 LLM (GPT-4 / Claude)
- [ ] 多模型路由 (成本优化)
- [ ] PRD 文档自动解析
- [ ] Figma 原型集成

### Phase 3 - 商业化
- [ ] SaaS 平台
- [ ] 企业订阅系统
- [ ] 私有化人设库
- [ ] API 开放平台

---

## 📁 项目结构

```
personalab-demo/
├── backend/
│   ├── api.py              # FastAPI 服务
│   ├── agent_generator.py  # Agent 生成器
│   ├── sandbox_engine.py   # 推演引擎
│   └── requirements.txt    # Python 依赖
├── frontend/
│   └── index.html          # Web 前端
└── README.md
```

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
