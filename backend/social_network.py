"""
Agent Social Network - Agent 社交网络
实现 agent 之间的交流、影响和传播
"""

import random
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict


class InteractionType(Enum):
    """交互类型"""
    RECOMMEND = "recommend"      # 推荐
    COMPLAIN = "complain"        # 投诉
    SHARE = "share"              # 分享
    ASK = "ask"                  # 询问
    ANSWER = "answer"            # 回答
    INFLUENCE = "influence"      # 影响


@dataclass
class SocialConnection:
    """社交关系"""
    agent_a: str
    agent_b: str
    relationship: float  # -1 到 1，负面到正面
    interaction_count: int = 0
    trust_level: float = 0.5  # 信任度 0-1


@dataclass
class SocialEvent:
    """社交事件"""
    event_id: str
    event_type: InteractionType
    source_agent: str
    target_agents: List[str]
    content: str
    feature: str
    timestamp: datetime
    influence_score: float = 0.0  # 影响力分数


@dataclass
class AgentSocialState:
    """Agent 社交状态"""
    agent_id: str
    friends: Set[str] = field(default_factory=set)
    followers: Set[str] = field(default_factory=set)
    following: Set[str] = field(default_factory=set)
    
    # 社交影响力
    influence_power: float = 0.5  # 影响力 0-1
    susceptibility: float = 0.5   # 易受影响程度 0-1
    
    # 态度记录
    feature_attitudes: Dict[str, float] = field(default_factory=dict)  # feature -> -1 到 1
    
    # 互动历史
    recommendations_given: int = 0
    recommendations_received: int = 0
    complaints_heard: Dict[str, int] = field(default_factory=dict)  # feature -> count
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "friends_count": len(self.friends),
            "followers_count": len(self.followers),
            "influence_power": self.influence_power,
            "feature_attitudes": self.feature_attitudes,
            "recommendations_received": self.recommendations_received
        }


class SocialNetwork:
    """社交网络引擎"""
    
    def __init__(self, agent_count: int):
        self.agent_count = agent_count
        self.agent_states: Dict[str, AgentSocialState] = {}
        self.connections: Dict[Tuple[str, str], SocialConnection] = {}
        self.events: List[SocialEvent] = []
        self.event_id_counter = 0
        
        # 传播统计
        self.viral_coefficient = 0.0  # 病毒传播系数
        self.word_of_mouth_impact = 0.0  # 口碑影响
        
    def initialize_network(self, agent_ids: List[str]):
        """初始化社交网络"""
        for agent_id in agent_ids:
            self.agent_states[agent_id] = AgentSocialState(
                agent_id=agent_id,
                influence_power=random.uniform(0.2, 0.9),
                susceptibility=random.uniform(0.2, 0.9)
            )
        
        # 建立随机社交关系
        self._create_random_connections(agent_ids)
    
    def _create_random_connections(self, agent_ids: List[str]):
        """创建随机社交关系"""
        # 每个agent有3-10个朋友
        for agent_id in agent_ids:
            state = self.agent_states[agent_id]
            
            # 随机选择朋友
            potential_friends = [a for a in agent_ids if a != agent_id]
            num_friends = random.randint(3, min(10, len(potential_friends)))
            friends = random.sample(potential_friends, num_friends)
            
            state.friends.update(friends)
            
            # 建立双向连接
            for friend in friends:
                # 确保对称关系
                self.agent_states[friend].followers.add(agent_id)
                state.following.add(friend)
                
                # 创建连接记录
                key = (min(agent_id, friend), max(agent_id, friend))
                if key not in self.connections:
                    self.connections[key] = SocialConnection(
                        agent_a=key[0],
                        agent_b=key[1],
                        relationship=random.uniform(-0.3, 0.8),
                        trust_level=random.uniform(0.3, 0.9)
                    )
    
    def propagate_recommendation(
        self,
        source_id: str,
        feature: str,
        attitude: float,  # -1(负面) 到 1(正面)
        agent_profiles: Dict  # agent_id -> AgentProfile
    ) -> List[SocialEvent]:
        """传播推荐/投诉"""
        
        events = []
        source_state = self.agent_states.get(source_id)
        if not source_state:
            return events
        
        # 更新源agent的态度
        source_state.feature_attitudes[feature] = attitude
        
        # 决定传播范围
        if attitude > 0.3:
            # 正面推荐，传播给朋友
            targets = list(source_state.friends)
            event_type = InteractionType.RECOMMEND
        elif attitude < -0.3:
            # 负面投诉，传播给朋友和可能的潜在用户
            targets = list(source_state.friends)
            # 负面传播更广
            for friend in list(source_state.friends):
                targets.extend(list(self.agent_states[friend].friends)[:2])
            targets = list(set(targets))
            event_type = InteractionType.COMPLAIN
        else:
            # 中立，不传播
            return events
        
        # 创建传播事件
        event = SocialEvent(
            event_id=f"event_{self.event_id_counter}",
            event_type=event_type,
            source_agent=source_id,
            target_agents=targets,
            content=f"{'推荐' if attitude > 0 else '不推荐'} {feature}",
            feature=feature,
            timestamp=datetime.now(),
            influence_score=source_state.influence_power * abs(attitude)
        )
        self.event_id_counter += 1
        events.append(event)
        self.events.append(event)
        
        # 更新统计
        if event_type == InteractionType.RECOMMEND:
            source_state.recommendations_given += 1
        
        # 影响目标agent
        for target_id in targets:
            target_state = self.agent_states.get(target_id)
            if not target_id:
                continue
            
            # 计算影响强度
            influence = self._calculate_influence(
                source_id, target_id, attitude, feature
            )
            
            # 更新目标agent的态度
            if feature not in target_state.feature_attitudes:
                target_state.feature_attitudes[feature] = 0.0
            
            # 易受影响的agent更容易被影响
            old_attitude = target_state.feature_attitudes[feature]
            new_attitude = old_attitude + influence * target_state.susceptibility
            target_state.feature_attitudes[feature] = max(-1, min(1, new_attitude))
            
            # 记录投诉
            if event_type == InteractionType.COMPLAIN:
                target_state.complaints_heard[feature] = \
                    target_state.complaints_heard.get(feature, 0) + 1
            
            # 记录推荐
            if event_type == InteractionType.RECOMMEND:
                target_state.recommendations_received += 1
        
        return events
    
    def _calculate_influence(
        self,
        source_id: str,
        target_id: str,
        attitude: float,
        feature: str
    ) -> float:
        """计算影响强度"""
        
        # 基础影响
        influence = attitude * 0.3
        
        # 关系强度加成
        key = (min(source_id, target_id), max(source_id, target_id))
        connection = self.connections.get(key)
        if connection:
            # 正面关系增强正面传播，削弱负面传播
            if attitude > 0:
                influence *= (0.5 + connection.relationship * 0.5)
            else:
                influence *= (0.5 + connection.trust_level * 0.5)
        
        # 影响力加成
        source_state = self.agent_states.get(source_id)
        if source_state:
            influence *= source_state.influence_power
        
        return influence
    
    def simulate_word_of_mouth(
        self,
        agent_profiles: Dict,
        features: List[str],
        day: int
    ) -> Dict:
        """模拟口碑传播"""
        
        results = {
            "total_recommendations": 0,
            "total_complaints": 0,
            "feature_virality": {},
            "influenced_agents": set()
        }
        
        for feature in features:
            # 找出对该功能有态度的agent
            attitudes = []
            for agent_id, state in self.agent_states.items():
                if feature in state.feature_attitudes:
                    attitudes.append((agent_id, state.feature_attitudes[feature]))
            
            # 随机选择一些agent进行传播
            propagators = random.sample(
                attitudes,
                min(len(attitudes), max(5, len(attitudes) // 10))
            )
            
            feature_recs = 0
            feature_complaints = 0
            
            for agent_id, attitude in propagators:
                events = self.propagate_recommendation(
                    agent_id, feature, attitude, agent_profiles
                )
                
                for event in events:
                    if event.event_type == InteractionType.RECOMMEND:
                        feature_recs += 1
                        results["influenced_agents"].update(event.target_agents)
                    else:
                        feature_complaints += 1
                        results["influenced_agents"].update(event.target_agents)
            
            results["feature_virality"][feature] = {
                "recommendations": feature_recs,
                "complaints": feature_complaints,
                "net_sentiment": feature_recs - feature_complaints * 2  # 负面权重更高
            }
            
            results["total_recommendations"] += feature_recs
            results["total_complaints"] += feature_complaints
        
        results["influenced_agents"] = list(results["influenced_agents"])
        
        # 计算病毒系数
        if len(results["influenced_agents"]) > 0:
            self.viral_coefficient = len(results["influenced_agents"]) / self.agent_count
            self.word_of_mouth_impact = results["total_recommendations"] / max(1, results["total_complaints"])
        
        return results
    
    def get_trending_features(self) -> List[Tuple[str, float]]:
        """获取热门功能排名"""
        
        feature_sentiment = defaultdict(list)
        
        for state in self.agent_states.values():
            for feature, attitude in state.feature_attitudes.items():
                feature_sentiment[feature].append(attitude)
        
        trending = []
        for feature, attitudes in feature_sentiment.items():
            avg_sentiment = sum(attitudes) / len(attitudes)
            reach = len(attitudes)
            score = avg_sentiment * (1 + reach / self.agent_count)
            trending.append((feature, score))
        
        return sorted(trending, key=lambda x: -x[1])
    
    def get_social_stats(self) -> Dict:
        """获取社交网络统计"""
        
        total_friends = sum(len(s.friends) for s in self.agent_states.values())
        avg_friends = total_friends / len(self.agent_states) if self.agent_states else 0
        
        return {
            "total_agents": len(self.agent_states),
            "total_connections": len(self.connections),
            "avg_friends_per_agent": round(avg_friends, 1),
            "total_events": len(self.events),
            "viral_coefficient": round(self.viral_coefficient, 3),
            "word_of_mouth_ratio": round(self.word_of_mouth_impact, 2)
        }


# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建社交网络
    agent_ids = [f"agent_{i}" for i in range(50)]
    network = SocialNetwork(50)
    network.initialize_network(agent_ids)
    
    print("=== 社交网络初始化 ===")
    print(network.get_social_stats())
    
    # 模拟传播
    print("\n=== 模拟口碑传播 ===")
    
    # Agent 0 推荐功能 A
    network.propagate_recommendation(
        "agent_0", "核心功能", 0.8, {}
    )
    
    # Agent 10 投诉功能 B
    network.propagate_recommendation(
        "agent_10", "高级功能", -0.6, {}
    )
    
    print(f"传播后事件数: {len(network.events)}")
    print(f"病毒系数: {network.viral_coefficient}")
    
    print("\n=== 热门功能 ===")
    for feature, score in network.get_trending_features():
        print(f"  {feature}: {score:.2f}")
