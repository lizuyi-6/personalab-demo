# PersonaLab 变更日志

## v0.4 (2026-04-07)

### 🆕 新功能

**Agent 社区系统**
- 真实的社区生态：发帖、评论、点赞、分享
- 用户等级系统：新人/活跃/达人/KOL
- 热门内容推荐：Reddit 风格热度算法
- 功能情感分析：基于社区内容分析用户态度
- 社交关系：关注、粉丝、好友

**新增指标**
- `total_posts`: 发帖总数
- `total_comments`: 评论总数
- `active_users`: 活跃用户数
- `level_distribution`: 用户等级分布
- `feature_sentiments`: 功能情感分析
- `trending_features`: 热门话题

**新增文件**
- `backend/community.py`: 完整社区系统

### 🔧 技术细节

```python
# 社区初始化
community = CommunitySystem("产品社区")
community.initialize_community(agent_profiles)

# 模拟用户活动
community.simulate_user_activity(
    user_id, features, mood, agent_profile
)

# 获取热门内容
hot_posts = community.get_hot_posts()

# 功能情感分析
sentiment = community.get_feature_sentiment("核心功能")
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
