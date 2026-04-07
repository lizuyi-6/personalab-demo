# PersonaLab 变更日志

## v0.4 (开发中)

### 🆕 新功能

**Agent 社交网络**
- Agent 之间可以建立社交关系（朋友、关注）
- 支持口碑传播：推荐/投诉影响朋友
- 病毒系数计算：衡量产品传播力
- 社交影响力：高影响力 Agent 影响更多人

**新增指标**
- `social_interactions`: 社交互动次数
- `word_of_mouth_reach`: 口碑传播覆盖人数
- `viral_coefficient`: 病毒传播系数
- `trending_features`: 社交热度排行

**新增文件**
- `backend/social_network.py`: 社交网络引擎

### 🔧 技术细节

```python
# 社交网络初始化
network = SocialNetwork(agent_count)
network.initialize_network(agent_ids)

# 口碑传播
network.propagate_recommendation(
    source_id, feature, attitude, agent_profiles
)

# 获取热度排行
trending = network.get_trending_features()
```

---

## v0.3 (2026-04-07)

### 新功能

- PRD 自动生成器
- 四步向导 UI
- PRD 编辑确认流程

---

## v0.2 (2026-04-07)

### 新功能

- LLM 路由器
- PRD 解析器
- 报告生成器
- 可视化图表

---

## v0.1 (2026-04-07)

### 初始版本

- OCEAN 人格模型
- 沙盘推演引擎
- Web 前端 Demo
