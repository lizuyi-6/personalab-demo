"""
OCEAN Personality Model Agent Generator
基于五大人格模型生成拟态用户
"""

import random
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class OCEANPersonality:
    """OCEAN 五因素人格模型"""
    openness: float          # 开放性 (0-1) - 好奇心、创造力
    conscientiousness: float # 尽责性 (0-1) - 自律、可靠性
    extraversion: float      # 外向性 (0-1) - 社交、活跃度
    agreeableness: float     # 宜人性 (0-1) - 合作、信任
    neuroticism: float       # 神经质 (0-1) - 情绪稳定性

    def to_prompt_traits(self) -> str:
        """转换为 prompt 可用的性格描述"""
        traits = []
        
        if self.openness > 0.7:
            traits.append("好奇心强、喜欢尝试新事物、富有创造力")
        elif self.openness < 0.3:
            traits.append("偏好熟悉的事物、务实、传统")
            
        if self.conscientiousness > 0.7:
            traits.append("高度自律、注重细节、目标导向")
        elif self.conscientiousness < 0.3:
            traits.append("随性、灵活、有时拖延")
            
        if self.extraversion > 0.7:
            traits.append("外向活跃、喜欢社交、表达欲强")
        elif self.extraversion < 0.3:
            traits.append("内向安静、独处充电、深思熟虑")
            
        if self.agreeableness > 0.7:
            traits.append("友善合作、乐于助人、信任他人")
        elif self.agreeableness < 0.3:
            traits.append("挑剔批判、竞争意识强、怀疑倾向")
            
        if self.neuroticism > 0.7:
            traits.append("情绪敏感、容易焦虑、反应强烈")
        elif self.neuroticism < 0.3:
            traits.append("情绪稳定、抗压能力强、心态平和")
            
        return "、".join(traits) if traits else "性格平衡"


@dataclass
class AgentProfile:
    """拟态用户画像"""
    id: str
    name: str
    age: int
    occupation: str
    personality: OCEANPersonality
    income_level: str      # low/medium/high
    tech_savvy: float      # 技术熟练度 0-1
    pain_points: List[str]
    daily_screen_time: int  # 小时
    preferred_platforms: List[str]
    
    # 动态状态
    attention_budget: float  # 当前可用注意力 (0-100)
    wallet_balance: float    # 虚拟钱包
    mood: float              # 情绪状态 (-1 到 1)
    fatigue: float           # 疲劳度 (0-1)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['personality'] = asdict(self.personality)
        return data
    
    def to_simulation_prompt(self) -> str:
        """生成用于模拟的完整 prompt"""
        return f"""你是一个真实用户的数字分身，请完全沉浸在这个角色中。

## 基础信息
- 姓名：{self.name}
- 年龄：{self.age}岁
- 职业：{self.occupation}
- 收入水平：{self.income_level}
- 技术熟练度：{'精通' if self.tech_savvy > 0.7 else '一般' if self.tech_savvy > 0.3 else '新手'}

## 性格特点
{self.personality.to_prompt_traits()}

## 痛点与需求
{chr(10).join(f'- {p}' for p in self.pain_points)}

## 使用习惯
- 日均屏幕时间：{self.daily_screen_time}小时
- 常用平台：{', '.join(self.preferred_platforms)}

## 当前状态
- 注意力余额：{self.attention_budget:.0f}/100
- 情绪：{'积极' if self.mood > 0.3 else '一般' if self.mood > -0.3 else '消极'}
- 疲劳度：{'高' if self.fatigue > 0.7 else '中' if self.fatigue > 0.3 else '低'}

## 行为约束
1. 你有有限的注意力和时间，不会对每个功能都感兴趣
2. 你会根据性格特点做出真实的反应（包括负面反馈）
3. 如果产品不好用，你会表达不满甚至放弃
4. 如果产品让你惊喜，你会主动分享给朋友
5. 不要讨好产品方，保持真实用户的挑剔和惰性
"""


class AgentGenerator:
    """Agent 生成器"""
    
    OCCUPATIONS = [
        "产品经理", "程序员", "设计师", "运营", "市场",
        "学生", "教师", "医生", "销售", "自由职业",
        "创业者", "HR", "财务", "行政", "记者"
    ]
    
    PAIN_POINTS_POOL = [
        "时间不够用", "工作效率低", "信息过载", "决策困难",
        "缺乏动力", "社交焦虑", "经济压力", "学习曲线陡峭",
        "找不到好工具", "团队协作困难", "数据安全担忧", "隐私顾虑",
        "界面太复杂", "功能太少", "价格太贵", "客服响应慢"
    ]
    
    PLATFORMS = [
        "微信", "抖音", "小红书", "B站", "微博",
        "知乎", "淘宝", "京东", "美团", "钉钉"
    ]
    
    @classmethod
    def generate_agent(
        cls,
        personality: Optional[OCEANPersonality] = None,
        constraints: Optional[Dict] = None
    ) -> AgentProfile:
        """生成单个 Agent"""
        
        constraints = constraints or {}
        
        # 生成或使用指定的人格
        if personality is None:
            personality = OCEANPersonality(
                openness=random.uniform(0, 1),
                conscientiousness=random.uniform(0, 1),
                extraversion=random.uniform(0, 1),
                agreeableness=random.uniform(0, 1),
                neuroticism=random.uniform(0, 1)
            )
        
        # 根据人格调整其他属性
        age = constraints.get('age', random.randint(18, 55))
        tech_savvy = constraints.get('tech_savvy', 
            min(1.0, max(0.1, personality.openness * 0.6 + random.uniform(0, 0.4))))
        
        # 选择痛点（根据性格）
        num_pain_points = random.randint(1, 3)
        pain_points = random.sample(cls.PAIN_POINTS_POOL, num_pain_points)
        
        # 选择平台
        num_platforms = random.randint(2, 5)
        preferred_platforms = random.sample(cls.PLATFORMS, num_platforms)
        
        # 生成名字（简化版）
        first_names = ["张", "王", "李", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        last_names = ["伟", "芳", "娜", "敏", "强", "磊", "洋", "艳", "勇", "杰"]
        name = random.choice(first_names) + random.choice(last_names)
        
        # 收入水平
        income_map = {0: "low", 1: "medium", 2: "high"}
        income_level = income_map.get(constraints.get('income'), 
            random.choices(["low", "medium", "high"], weights=[0.3, 0.5, 0.2])[0])
        
        return AgentProfile(
            id=str(uuid.uuid4())[:8],
            name=name,
            age=age,
            occupation=constraints.get('occupation', random.choice(cls.OCCUPATIONS)),
            personality=personality,
            income_level=income_level,
            tech_savvy=tech_savvy,
            pain_points=pain_points,
            daily_screen_time=random.randint(3, 10),
            preferred_platforms=preferred_platforms,
            attention_budget=100.0,
            wallet_balance=random.uniform(100, 5000),
            mood=random.uniform(-0.3, 0.5),
            fatigue=random.uniform(0, 0.3)
        )
    
    @classmethod
    def generate_population(
        cls,
        count: int = 100,
        distribution: Optional[Dict] = None
    ) -> List[AgentProfile]:
        """生成一批 Agent"""
        agents = []
        distribution = distribution or {}
        
        for _ in range(count):
            agent = cls.generate_agent(
                personality=None,
                constraints=distribution
            )
            agents.append(agent)
        
        return agents


# 测试
if __name__ == "__main__":
    # 生成10个Agent
    agents = AgentGenerator.generate_population(10)
    
    for agent in agents[:3]:
        print(f"\n{'='*50}")
        print(f"Agent: {agent.name} ({agent.age}岁, {agent.occupation})")
        print(f"性格: O={agent.personality.openness:.2f}, "
              f"C={agent.personality.conscientiousness:.2f}, "
              f"E={agent.personality.extraversion:.2f}, "
              f"A={agent.personality.agreeableness:.2f}, "
              f"N={agent.personality.neuroticism:.2f}")
        print(f"痛点: {', '.join(agent.pain_points)}")
        print(f"\n--- 模拟Prompt ---")
        print(agent.to_simulation_prompt())
