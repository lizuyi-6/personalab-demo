"""
PersonaLab 沙盘推演引擎
支持多Agent并发交互和产品评估
"""

import asyncio
import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid

from agent_generator import AgentProfile, AgentGenerator
from social_network import SocialNetwork, InteractionType


class ActionType(Enum):
    """Agent 行为类型"""
    VIEW = "view"              # 浏览
    CLICK = "click"            # 点击
    SIGNUP = "signup"          # 注册
    PURCHASE = "purchase"      # 购买
    SHARE = "share"            # 分享
    COMPLAIN = "complain"      # 投诉
    ABANDON = "abandon"        # 放弃
    PRAISE = "praise"          # 好评
    IGNORE = "ignore"          # 忽略


@dataclass
class Action:
    """单个行为记录"""
    agent_id: str
    action_type: ActionType
    target: str              # 目标功能/页面
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    feedback: str = ""       # 用户反馈/吐槽


@dataclass
class SimulationConfig:
    """模拟配置"""
    product_name: str
    product_description: str
    features: List[Dict]          # 功能列表
    virtual_days: int = 7          # 虚拟天数
    time_scale: float = 0.001      # 时间加速比例 (1虚拟天 = 0.001真实天 ≈ 1.4分钟)
    max_actions_per_day: int = 20  # 每天最大行为数


@dataclass
class SimulationResult:
    """模拟结果"""
    session_id: str
    config: SimulationConfig
    actions: List[Action]
    metrics: Dict
    insights: List[str]
    start_time: datetime
    end_time: datetime
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "config": {
                "product_name": self.config.product_name,
                "virtual_days": self.config.virtual_days,
            },
            "metrics": self.metrics,
            "insights": self.insights,
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "total_actions": len(self.actions)
        }


class RealismEngine:
    """真实性校验引擎 - 引入博弈论约束"""
    
    @staticmethod
    def calculate_attention_cost(action: ActionType, agent: AgentProfile) -> float:
        """计算注意力消耗"""
        base_costs = {
            ActionType.VIEW: 5,
            ActionType.CLICK: 10,
            ActionType.SIGNUP: 30,
            ActionType.PURCHASE: 50,
            ActionType.SHARE: 20,
            ActionType.COMPLAIN: 15,
            ActionType.ABANDON: 5,
            ActionType.PRAISE: 10,
            ActionType.IGNORE: 0
        }
        
        cost = base_costs.get(action, 10)
        
        # 根据性格调整
        # 低尽责性的人更容易分心，消耗更多注意力
        if agent.personality.conscientiousness < 0.3:
            cost *= 1.3
        
        # 高神经质的人在复杂操作上消耗更多
        if action in [ActionType.SIGNUP, ActionType.PURCHASE]:
            if agent.personality.neuroticism > 0.7:
                cost *= 1.5
        
        return cost
    
    @staticmethod
    def update_mood(agent: AgentProfile, action: ActionType, success: bool) -> float:
        """更新情绪状态"""
        mood_delta = 0
        
        if success:
            if action == ActionType.PURCHASE:
                mood_delta = random.uniform(0.1, 0.3)
            elif action == ActionType.SHARE:
                mood_delta = random.uniform(0.15, 0.25)
            elif action == ActionType.PRAISE:
                mood_delta = random.uniform(0.05, 0.15)
        else:
            if action == ActionType.ABANDON:
                mood_delta = random.uniform(-0.3, -0.1)
            elif action == ActionType.COMPLAIN:
                mood_delta = random.uniform(-0.2, -0.05)
        
        # 高神经质的人情绪波动更大
        if agent.personality.neuroticism > 0.7:
            mood_delta *= 1.5
        
        agent.mood = max(-1, min(1, agent.mood + mood_delta))
        return agent.mood
    
    @staticmethod
    def update_fatigue(agent: AgentProfile, actions_today: int) -> float:
        """更新疲劳度"""
        # 每个行为增加疲劳
        agent.fatigue = min(1.0, agent.fatigue + 0.05)
        
        # 高外向性的人更抗疲劳
        if agent.personality.extraversion > 0.7:
            agent.fatigue *= 0.9
        
        return agent.fatigue
    
    @staticmethod
    def should_abandon(agent: AgentProfile, consecutive_failures: int) -> bool:
        """判断是否应该放弃"""
        # 基础放弃概率
        base_prob = 0.1 + consecutive_failures * 0.15
        
        # 低尽责性 + 高神经质 = 更容易放弃
        if agent.personality.conscientiousness < 0.3:
            base_prob += 0.2
        if agent.personality.neuroticism > 0.7:
            base_prob += 0.15
        
        # 疲劳度高增加放弃概率
        if agent.fatigue > 0.7:
            base_prob += 0.2
        
        return random.random() < base_prob


class SandboxEngine:
    """沙盘推演引擎"""
    
    def __init__(self, config: SimulationConfig, agents: List[AgentProfile]):
        self.config = config
        self.agents = agents
        self.actions: List[Action] = []
        self.session_id = str(uuid.uuid4())[:8]
        self.realism = RealismEngine()
        
        # 社交网络
        self.social_network: Optional[SocialNetwork] = None
        
        # 统计数据
        self.stats = {
            "signups": 0,
            "purchases": 0,
            "shares": 0,
            "complaints": 0,
            "abandonments": 0,
            "daily_active": set(),
            "feature_usage": {},
            "social_interactions": 0,
            "word_of_mouth_reach": 0,
        }
    
    async def simulate_agent_day(
        self,
        agent: AgentProfile,
        virtual_day: int
    ) -> List[Action]:
        """模拟单个Agent的一天"""
        
        actions = []
        actions_today = 0
        consecutive_failures = 0
        
        # 重置每日状态
        agent.attention_budget = 100.0
        agent.fatigue = max(0, agent.fatigue - 0.5)  # 休息后恢复
        
        for feature in self.config.features:
            # 检查是否还有注意力预算
            if agent.attention_budget < 10 or agent.fatigue > 0.8:
                break
            
            # 决定是否对这个功能感兴趣
            if not self._should_engage(agent, feature):
                actions.append(Action(
                    agent_id=agent.id,
                    action_type=ActionType.IGNORE,
                    target=feature["name"],
                    timestamp=datetime.now(),
                    feedback=f"不感兴趣"
                ))
                continue
            
            # 决定行为类型
            action_type = self._decide_action(agent, feature, virtual_day)
            
            # 计算注意力消耗
            attention_cost = self.realism.calculate_attention_cost(action_type, agent)
            
            if attention_cost > agent.attention_budget:
                # 注意力不足，简化行为
                action_type = ActionType.VIEW
                attention_cost = min(agent.attention_budget, 5)
            
            # 执行行为
            success = self._execute_action(agent, action_type, feature)
            
            # 更新状态
            agent.attention_budget -= attention_cost
            self.realism.update_mood(agent, action_type, success)
            self.realism.update_fatigue(agent, actions_today)
            
            # 生成反馈
            feedback = self._generate_feedback(agent, action_type, feature, success)
            
            # 记录行为
            action = Action(
                agent_id=agent.id,
                action_type=action_type,
                target=feature["name"],
                timestamp=datetime.now(),
                feedback=feedback
            )
            actions.append(action)
            self.actions.append(action)
            
            # 更新统计
            self._update_stats(action_type, agent.id)
            
            # 社交传播：好评或投诉时影响朋友
            if self.social_network:
                if action_type == ActionType.PRAISE or action_type == ActionType.SHARE:
                    # 正面传播
                    attitude = 0.5 + agent.mood * 0.3
                    self.social_network.propagate_recommendation(
                        agent.id, feature["name"], attitude, {}
                    )
                elif action_type == ActionType.COMPLAIN:
                    # 负面传播
                    attitude = -0.5 + agent.mood * 0.3
                    self.social_network.propagate_recommendation(
                        agent.id, feature["name"], attitude, {}
                    )
            
            actions_today += 1
            
            if not success:
                consecutive_failures += 1
            else:
                consecutive_failures = 0
            
            # 检查是否应该放弃
            if self.realism.should_abandon(agent, consecutive_failures):
                actions.append(Action(
                    agent_id=agent.id,
                    action_type=ActionType.ABANDON,
                    target="product",
                    timestamp=datetime.now(),
                    feedback="体验太差，不想用了"
                ))
                self.stats["abandonments"] += 1
                break
        
        return actions
    
    def _should_engage(self, agent: AgentProfile, feature: Dict) -> bool:
        """判断是否应该参与"""
        # 基于性格和功能匹配度
        base_prob = 0.5
        
        # 开放性高的人更愿意尝试新功能
        if agent.personality.openness > 0.7:
            base_prob += 0.2
        elif agent.personality.openness < 0.3:
            base_prob -= 0.2
        
        # 检查痛点匹配
        for pain_point in agent.pain_points:
            if pain_point in feature.get("solves", []):
                base_prob += 0.15
        
        return random.random() < base_prob
    
    def _decide_action(
        self,
        agent: AgentProfile,
        feature: Dict,
        virtual_day: int
    ) -> ActionType:
        """决定行为类型"""
        
        # 第一天更可能是浏览和注册
        if virtual_day == 1:
            weights = [0.4, 0.3, 0.2, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0]
        else:
            weights = [0.2, 0.3, 0.0, 0.15, 0.1, 0.1, 0.05, 0.1, 0.0]
        
        # 高宜人性更可能好评和分享
        if agent.personality.agreeableness > 0.7:
            weights[7] += 0.15  # praise
            weights[4] += 0.1   # share
        
        # 低宜人性更可能投诉
        if agent.personality.agreeableness < 0.3:
            weights[5] += 0.15  # complain
        
        # 标准化
        total = sum(weights)
        weights = [w / total for w in weights]
        
        action_types = list(ActionType)
        return random.choices(action_types, weights=weights)[0]
    
    def _execute_action(
        self,
        agent: AgentProfile,
        action_type: ActionType,
        feature: Dict
    ) -> bool:
        """执行行为，返回是否成功"""
        
        # 简化逻辑：基于技术熟练度和功能复杂度
        if action_type == ActionType.IGNORE:
            return True
        
        complexity = feature.get("complexity", 0.5)
        
        # 技术熟练度高的人更容易成功
        success_prob = agent.tech_savvy * 0.5 + (1 - complexity) * 0.3 + 0.2
        
        # 疲劳降低成功率
        success_prob *= (1 - agent.fatigue * 0.3)
        
        return random.random() < success_prob
    
    def _generate_feedback(
        self,
        agent: AgentProfile,
        action_type: ActionType,
        feature: Dict,
        success: bool
    ) -> str:
        """生成用户反馈/吐槽"""
        
        positive_templates = [
            "这个功能不错，解决了我的问题",
            "体验很流畅，赞一个",
            "终于有人做了这个功能！",
            "比我想象的好用",
            "会推荐给朋友"
        ]
        
        negative_templates = [
            "操作太复杂了，放弃",
            "加载太慢了",
            "找不到入口在哪",
            "这功能有什么用？",
            "Bug太多了吧",
            "不如竞品好用"
        ]
        
        neutral_templates = [
            "还行吧，勉强能用",
            "中规中矩",
            "有待改进"
        ]
        
        if success and action_type in [ActionType.PRAISE, ActionType.SHARE]:
            return random.choice(positive_templates)
        elif not success or action_type == ActionType.COMPLAIN:
            # 低宜人性的人吐槽更尖锐
            if agent.personality.agreeableness < 0.3:
                return random.choice(negative_templates) + "👎"
            return random.choice(negative_templates)
        else:
            return random.choice(neutral_templates)
    
    def _update_stats(self, action_type: ActionType, agent_id: str):
        """更新统计数据"""
        if action_type == ActionType.SIGNUP:
            self.stats["signups"] += 1
        elif action_type == ActionType.PURCHASE:
            self.stats["purchases"] += 1
        elif action_type == ActionType.SHARE:
            self.stats["shares"] += 1
        elif action_type == ActionType.COMPLAIN:
            self.stats["complaints"] += 1
        
        self.stats["daily_active"].add(agent_id)
    
    async def run(self) -> SimulationResult:
        """运行模拟"""
        
        start_time = datetime.now()
        
        # 初始化社交网络
        agent_ids = [agent.id for agent in self.agents]
        self.social_network = SocialNetwork(len(self.agents))
        self.social_network.initialize_network(agent_ids)
        
        # Agent ID -> AgentProfile 映射
        agent_map = {agent.id: agent for agent in self.agents}
        
        # 模拟每一天
        for day in range(1, self.config.virtual_days + 1):
            # 并发模拟所有Agent
            tasks = [
                self.simulate_agent_day(agent, day)
                for agent in self.agents
            ]
            await asyncio.gather(*tasks)
            
            # 每日社交互动（口碑传播）
            features = [f["name"] for f in self.config.features]
            social_result = self.social_network.simulate_word_of_mouth(
                agent_map, features, day
            )
            
            # 更新社交统计
            self.stats["social_interactions"] += social_result["total_recommendations"] + social_result["total_complaints"]
            self.stats["word_of_mouth_reach"] = len(social_result["influenced_agents"])
            
            # 每日重置活跃用户
            self.stats["daily_active"] = set()
        
        end_time = datetime.now()
        
        # 计算指标
        metrics = self._calculate_metrics()
        
        # 生成洞察
        insights = self._generate_insights()
        
        return SimulationResult(
            session_id=self.session_id,
            config=self.config,
            actions=self.actions,
            metrics=metrics,
            insights=insights,
            start_time=start_time,
            end_time=end_time
        )
    
    def _calculate_metrics(self) -> Dict:
        """计算核心指标"""
        total_agents = len(self.agents)
        
        # 转化率
        signup_rate = self.stats["signups"] / total_agents
        purchase_rate = self.stats["purchases"] / max(self.stats["signups"], 1)
        
        # 留存率（简化：检查是否有回头用户）
        agent_action_counts = {}
        for action in self.actions:
            agent_action_counts[action.agent_id] = agent_action_counts.get(action.agent_id, 0) + 1
        
        returning_users = sum(1 for count in agent_action_counts.values() if count > 3)
        retention_rate = returning_users / total_agents
        
        # NPS（净推荐值）
        promoters = self.stats["shares"]
        detractors = self.stats["complaints"] + self.stats["abandonments"]
        nps = ((promoters - detractors) / total_agents) * 100
        
        # 功能热度
        feature_usage = {}
        for action in self.actions:
            feature_usage[action.target] = feature_usage.get(action.target, 0) + 1
        
        # 社交网络指标
        social_metrics = {}
        if self.social_network:
            social_stats = self.social_network.get_social_stats()
            social_metrics = {
                "social_interactions": self.stats["social_interactions"],
                "word_of_mouth_reach": self.stats["word_of_mouth_reach"],
                "viral_coefficient": social_stats.get("viral_coefficient", 0),
                "avg_friends": social_stats.get("avg_friends_per_agent", 0)
            }
            
            # 热门功能（社交传播）
            trending = self.social_network.get_trending_features()
            if trending:
                social_metrics["trending_features"] = [
                    {"name": f, "score": round(s, 2)} for f, s in trending[:3]
                ]
        
        return {
            "total_agents": total_agents,
            "total_actions": len(self.actions),
            "signup_rate": round(signup_rate * 100, 1),
            "purchase_rate": round(purchase_rate * 100, 1),
            "retention_rate": round(retention_rate * 100, 1),
            "nps": round(nps, 1),
            "complaint_rate": round(self.stats["complaints"] / total_agents * 100, 1),
            "abandonment_rate": round(self.stats["abandonments"] / total_agents * 100, 1),
            "feature_usage": feature_usage,
            "social_network": social_metrics
        }
    
    def _generate_insights(self) -> List[str]:
        """生成洞察建议"""
        insights = []
        metrics = self._calculate_metrics()
        
        # 注册率分析
        if metrics["signup_rate"] < 30:
            insights.append("⚠️ 注册率偏低，建议简化注册流程，减少必填项")
        
        # 留存率分析
        if metrics["retention_rate"] < 40:
            insights.append("⚠️ 留存率不足，用户缺乏持续使用的动力，考虑增加引导或激励")
        
        # NPS 分析
        if metrics["nps"] < 0:
            insights.append("🔴 NPS为负，产品存在严重问题，需要立即检查高频投诉点")
        elif metrics["nps"] < 30:
            insights.append("🟡 NPS偏低，产品有改进空间")
        
        # 放弃率分析
        if metrics["abandonment_rate"] > 20:
            insights.append("⚠️ 放弃率过高，可能存在体验断层或核心价值不清晰")
        
        # 功能热度分析
        feature_usage = metrics.get("feature_usage", {})
        if feature_usage:
            hot_features = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)
            insights.append(f"🔥 热门功能：{hot_features[0][0]}")
            
            cold_features = [f for f, c in feature_usage.items() if c < len(self.agents) * 0.1]
            if cold_features:
                insights.append(f"❄️ 冷门功能：{', '.join(cold_features)}，考虑下线或优化")
        
        if not insights:
            insights.append("✅ 产品整体表现良好，建议进行更大规模测试验证")
        
        return insights


# 测试运行
if __name__ == "__main__":
    async def test():
        # 创建模拟配置
        config = SimulationConfig(
            product_name="测试产品",
            product_description="一个简单的测试",
            features=[
                {"name": "核心功能A", "complexity": 0.3, "solves": ["时间不够用"]},
                {"name": "高级功能B", "complexity": 0.7, "solves": ["工作效率低"]},
                {"name": "社交功能C", "complexity": 0.5, "solves": ["社交焦虑"]},
            ],
            virtual_days=3
        )
        
        # 生成Agent
        agents = AgentGenerator.generate_population(20)
        
        # 运行模拟
        engine = SandboxEngine(config, agents)
        result = await engine.run()
        
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        print("\n洞察：")
        for insight in result.insights:
            print(f"  {insight}")
    
    asyncio.run(test())
