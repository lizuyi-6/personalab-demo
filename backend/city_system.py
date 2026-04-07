"""
PersonaLab City - 城市生态系统
复刻现实世界的职业、时间、经济、社交圈层
"""

import random
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from collections import defaultdict


# ============ 职业系统 ============

class Occupation(Enum):
    """职业类型"""
    # 科技行业
    SOFTWARE_ENGINEER = "软件工程师"
    PRODUCT_MANAGER = "产品经理"
    DESIGNER = "设计师"
    DATA_ANALYST = "数据分析师"
    
    # 商业
    ENTREPRENEUR = "创业者"
    MARKETING = "市场运营"
    SALES = "销售"
    HR = "人力资源"
    
    # 教育
    TEACHER = "教师"
    STUDENT = "学生"
    RESEARCHER = "研究员"
    
    # 服务行业
    DOCTOR = "医生"
    LAWYER = "律师"
    JOURNALIST = "记者"
    FREELANCER = "自由职业"
    
    # 其他
    CIVIL_SERVANT = "公务员"
    FINANCE = "金融从业者"
    OTHER = "其他"


@dataclass
class OccupationProfile:
    """职业画像"""
    occupation: Occupation
    avg_income: int          # 月收入
    income_variance: float   # 收入波动
    work_hours: Tuple[int, int]  # 工作时间 (start, end)
    tech_savvy_base: float   # 技术熟练度基础
    social_influence: float  # 社交影响力
    free_time_hours: float   # 每日空闲时间
    consumption_pattern: Dict  # 消费偏好


# 职业配置
OCCUPATION_CONFIGS = {
    Occupation.SOFTWARE_ENGINEER: OccupationProfile(
        occupation=Occupation.SOFTWARE_ENGINEER,
        avg_income=25000,
        income_variance=0.3,
        work_hours=(9, 21),
        tech_savvy_base=0.9,
        social_influence=0.5,
        free_time_hours=3,
        consumption_pattern={"科技产品": 0.4, "娱乐": 0.3, "学习": 0.2}
    ),
    Occupation.PRODUCT_MANAGER: OccupationProfile(
        occupation=Occupation.PRODUCT_MANAGER,
        avg_income=22000,
        income_variance=0.2,
        work_hours=(9, 20),
        tech_savvy_base=0.7,
        social_influence=0.7,
        free_time_hours=4,
        consumption_pattern={"效率工具": 0.5, "社交": 0.3, "学习": 0.2}
    ),
    Occupation.DESIGNER: OccupationProfile(
        occupation=Occupation.DESIGNER,
        avg_income=18000,
        income_variance=0.3,
        work_hours=(10, 20),
        tech_savvy_base=0.6,
        social_influence=0.6,
        free_time_hours=4,
        consumption_pattern={"设计工具": 0.4, "娱乐": 0.3, "艺术": 0.3}
    ),
    Occupation.ENTREPRENEUR: OccupationProfile(
        occupation=Occupation.ENTREPRENEUR,
        avg_income=30000,
        income_variance=0.8,
        work_hours=(8, 22),
        tech_savvy_base=0.7,
        social_influence=0.9,
        free_time_hours=2,
        consumption_pattern={"商业工具": 0.5, "社交": 0.4, "学习": 0.1}
    ),
    Occupation.STUDENT: OccupationProfile(
        occupation=Occupation.STUDENT,
        avg_income=1500,
        income_variance=0.5,
        work_hours=(8, 18),
        tech_savvy_base=0.8,
        social_influence=0.4,
        free_time_hours=6,
        consumption_pattern={"学习工具": 0.4, "娱乐": 0.4, "社交": 0.2}
    ),
    Occupation.TEACHER: OccupationProfile(
        occupation=Occupation.TEACHER,
        avg_income=12000,
        income_variance=0.1,
        work_hours=(7, 18),
        tech_savvy_base=0.5,
        social_influence=0.6,
        free_time_hours=5,
        consumption_pattern={"教育": 0.5, "生活": 0.3, "学习": 0.2}
    ),
    Occupation.DOCTOR: OccupationProfile(
        occupation=Occupation.DOCTOR,
        avg_income=28000,
        income_variance=0.2,
        work_hours=(8, 20),
        tech_savvy_base=0.6,
        social_influence=0.8,
        free_time_hours=3,
        consumption_pattern={"健康": 0.3, "效率工具": 0.3, "学习": 0.4}
    ),
    Occupation.FREELANCER: OccupationProfile(
        occupation=Occupation.FREELANCER,
        avg_income=15000,
        income_variance=0.6,
        work_hours=(10, 22),
        tech_savvy_base=0.7,
        social_influence=0.5,
        free_time_hours=6,
        consumption_pattern={"效率工具": 0.4, "娱乐": 0.3, "学习": 0.3}
    ),
}


# ============ 城市居民 ============

@dataclass
class CityResident:
    """城市居民"""
    resident_id: str
    name: str
    age: int
    occupation: Occupation
    occupation_profile: OccupationProfile
    
    # 经济状况
    monthly_income: int
    monthly_expense: int
    savings: float
    disposable_income: float  # 可支配收入
    
    # 时间分配
    work_schedule: Dict[int, List[str]]  # day -> [activities]
    daily_routine: Dict[str, str]  # time_slot -> activity
    
    # 社交圈层
    primary_circle: str    # 主圈层 (职业圈)
    secondary_circle: str  # 副圈层 (兴趣圈)
    social_connections: Set[str]  # 社交连接
    
    # 产品使用
    products_used: Dict[str, Dict]  # product -> usage_data
    product_interests: List[str]
    
    # 影响力
    klout_score: float  # 社交影响力分数
    early_adopter_tendency: float  # 早期采用倾向
    
    # 生活状态
    life_satisfaction: float
    work_life_balance: float
    tech_adoption_level: str  # early/early_majority/late/laggard
    
    def to_dict(self) -> Dict:
        return {
            "resident_id": self.resident_id,
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation.value,
            "monthly_income": self.monthly_income,
            "klout_score": round(self.klout_score, 2),
            "tech_adoption": self.tech_adoption_level,
            "primary_circle": self.primary_circle,
            "products_used": list(self.products_used.keys())
        }


# ============ 城市系统 ============

class CitySystem:
    """城市生态系统"""
    
    def __init__(self, city_name: str = "PersonaLab City"):
        self.city_name = city_name
        self.residents: Dict[str, CityResident] = {}
        
        # 圈层
        self.circles: Dict[str, Set[str]] = defaultdict(set)  # circle -> resident_ids
        
        # 产品市场
        self.product_market: Dict[str, Dict] = {}  # product -> market_data
        
        # 时间系统
        self.current_day = 0
        self.current_hour = 0
        
        # 统计
        self.stats = {
            "total_residents": 0,
            "occupation_distribution": defaultdict(int),
            "income_distribution": {"低": 0, "中": 0, "高": 0},
            "adoption_distribution": defaultdict(int),
        }
    
    def populate_city(self, population_size: int):
        """填充城市人口"""
        
        for i in range(population_size):
            resident = self._generate_resident(i)
            self.residents[resident.resident_id] = resident
            
            # 加入圈层
            self.circles[resident.primary_circle].add(resident.resident_id)
            self.circles[resident.secondary_circle].add(resident.resident_id)
        
        self._update_stats()
    
    def _generate_resident(self, index: int) -> CityResident:
        """生成城市居民"""
        
        # 随机职业
        occupations = list(OCCUPATION_CONFIGS.keys())
        occupation = random.choices(
            occupations,
            weights=[3, 3, 2, 2, 3, 4, 1, 2]  # 权重
        )[0]
        
        profile = OCCUPATION_CONFIGS.get(occupation, list(OCCUPATION_CONFIGS.values())[0])
        
        # 基本信息
        age = self._generate_age_for_occupation(occupation)
        name = self._generate_name()
        
        # 收入
        income = int(profile.avg_income * random.uniform(
            1 - profile.income_variance, 
            1 + profile.income_variance
        ))
        
        # 可支配收入
        expense = int(income * random.uniform(0.5, 0.8))
        disposable = income - expense
        
        # 社交圈层
        primary_circle = f"{occupation.value}圈"
        interests = ["科技", "艺术", "运动", "阅读", "游戏", "投资"]
        secondary_circle = random.choice(interests) + "圈"
        
        # 影响力
        klout = min(100, profile.social_influence * 100 * random.uniform(0.5, 1.5))
        
        # 技术采用
        tech_base = profile.tech_savvy_base
        if tech_base > 0.8:
            adoption = random.choices(
                ["early", "early_majority", "late", "laggard"],
                weights=[0.4, 0.4, 0.15, 0.05]
            )[0]
        elif tech_base > 0.6:
            adoption = random.choices(
                ["early", "early_majority", "late", "laggard"],
                weights=[0.2, 0.5, 0.25, 0.05]
            )[0]
        else:
            adoption = random.choices(
                ["early", "early_majority", "late", "laggard"],
                weights=[0.05, 0.3, 0.45, 0.2]
            )[0]
        
        return CityResident(
            resident_id=f"resident_{index}",
            name=name,
            age=age,
            occupation=occupation,
            occupation_profile=profile,
            monthly_income=income,
            monthly_expense=expense,
            savings=income * random.uniform(0, 12),
            disposable_income=disposable,
            work_schedule={},
            daily_routine=self._generate_routine(profile),
            primary_circle=primary_circle,
            secondary_circle=secondary_circle,
            social_connections=set(),
            klout_score=klout,
            early_adopter_tendency=1.0 if adoption == "early" else 0.5,
            life_satisfaction=random.uniform(0.4, 0.9),
            work_life_balance=random.uniform(0.3, 0.8),
            tech_adoption_level=adoption,
            products_used={},
            product_interests=[]
        )
    
    def _generate_age_for_occupation(self, occupation: Occupation) -> int:
        """根据职业生成年龄"""
        if occupation == Occupation.STUDENT:
            return random.randint(18, 25)
        elif occupation == Occupation.ENTREPRENEUR:
            return random.randint(25, 45)
        else:
            return random.randint(22, 55)
    
    def _generate_name(self) -> str:
        """生成姓名"""
        surnames = ["张", "王", "李", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        names = ["伟", "芳", "娜", "敏", "强", "磊", "洋", "艳", "勇", "杰"]
        return random.choice(surnames) + random.choice(names)
    
    def _generate_routine(self, profile: OccupationProfile) -> Dict[str, str]:
        """生成日常作息"""
        work_start, work_end = profile.work_hours
        
        routine = {}
        
        # 早晨
        routine["morning"] = "通勤" if work_start < 10 else "锻炼"
        
        # 工作时间
        routine["work"] = f"{work_start}:00-{work_end}:00 工作"
        
        # 晚间
        if work_end < 20:
            routine["evening"] = random.choice(["娱乐", "学习", "社交"])
        else:
            routine["evening"] = "加班"
        
        # 睡眠
        routine["sleep"] = f"23:{random.randint(0, 59):02d} 就寝"
        
        return routine
    
    def _update_stats(self):
        """更新统计"""
        self.stats["total_residents"] = len(self.residents)
        
        for resident in self.residents.values():
            self.stats["occupation_distribution"][resident.occupation.value] += 1
            
            if resident.monthly_income < 10000:
                self.stats["income_distribution"]["低"] += 1
            elif resident.monthly_income < 25000:
                self.stats["income_distribution"]["中"] += 1
            else:
                self.stats["income_distribution"]["高"] += 1
            
            self.stats["adoption_distribution"][resident.tech_adoption_level] += 1
    
    # ============ 产品传播 ============
    
    def introduce_product(self, product: Dict):
        """引入新产品到城市"""
        product_name = product.get("name", "未命名产品")
        
        self.product_market[product_name] = {
            "product": product,
            "total_users": 0,
            "daily_new_users": 0,
            "user_demographics": defaultdict(int),
            "adoption_curve": [],
            "revenue": 0
        }
    
    def simulate_product_adoption(
        self,
        product_name: str,
        days: int = 7
    ) -> Dict:
        """模拟产品在城市中的传播"""
        
        if product_name not in self.product_market:
            return {"error": "产品不存在"}
        
        product_data = self.product_market[product_name]
        product = product_data["product"]
        
        daily_stats = []
        
        for day in range(1, days + 1):
            day_new_users = 0
            day_active_users = 0
            
            for resident in self.residents.values():
                # 判断是否采用产品
                if product_name in resident.products_used:
                    day_active_users += 1
                    continue
                
                # 采用概率
                adopt_prob = self._calculate_adoption_probability(resident, product, day)
                
                if random.random() < adopt_prob:
                    # 采用产品
                    resident.products_used[product_name] = {
                        "adopted_day": day,
                        "usage_frequency": random.uniform(0.2, 0.8),
                        "satisfaction": random.uniform(0.3, 0.9)
                    }
                    day_new_users += 1
                    
                    # 更新产品数据
                    product_data["user_demographics"][resident.occupation.value] += 1
            
            product_data["total_users"] += day_new_users
            product_data["daily_new_users"] = day_new_users
            product_data["adoption_curve"].append(day_new_users)
            
            daily_stats.append({
                "day": day,
                "new_users": day_new_users,
                "total_users": product_data["total_users"],
                "penetration_rate": product_data["total_users"] / len(self.residents)
            })
        
        return {
            "product": product_name,
            "total_users": product_data["total_users"],
            "penetration_rate": round(product_data["total_users"] / len(self.residents) * 100, 1),
            "daily_stats": daily_stats,
            "demographics": dict(product_data["user_demographics"])
        }
    
    def _calculate_adoption_probability(
        self,
        resident: CityResident,
        product: Dict,
        day: int
    ) -> float:
        """计算采用概率"""
        
        base_prob = 0.05
        
        # 技术采用倾向
        if resident.tech_adoption_level == "early":
            base_prob *= 3
        elif resident.tech_adoption_level == "early_majority":
            base_prob *= 1.5
        elif resident.tech_adoption_level == "laggard":
            base_prob *= 0.3
        
        # 收入匹配
        price = product.get("price", 0)
        if price > 0:
            affordability = resident.disposable_income / price
            if affordability > 10:
                base_prob *= 1.5
            elif affordability < 1:
                base_prob *= 0.1
        
        # 社交影响
        connections_with_product = sum(
            1 for conn_id in resident.social_connections
            if conn_id in self.residents and 
            product.get("name") in self.residents[conn_id].products_used
        )
        base_prob *= (1 + connections_with_product * 0.2)
        
        # 圈层影响
        circle = resident.primary_circle
        circle_users = 0
        for rid in self.circles.get(circle, []):
            if rid in self.residents:
                if product.get("name") in self.residents[rid].products_used:
                    circle_users += 1
        
        if len(self.circles.get(circle, [])) > 0:
            circle_penetration = circle_users / len(self.circles[circle])
            base_prob *= (1 + circle_penetration)
        
        # 时间衰减（早期概率高）
        time_factor = max(0.5, 1 - day * 0.05)
        base_prob *= time_factor
        
        return min(0.8, base_prob)
    
    # ============ 城市分析 ============
    
    def get_city_overview(self) -> Dict:
        """获取城市概览"""
        
        return {
            "city_name": self.city_name,
            "population": self.stats["total_residents"],
            "occupation_distribution": dict(self.stats["occupation_distribution"]),
            "income_distribution": self.stats["income_distribution"],
            "adoption_distribution": dict(self.stats["adoption_distribution"]),
            "circles_count": len(self.circles),
            "products_in_market": list(self.product_market.keys())
        }
    
    def get_product_market_report(self, product_name: str) -> Dict:
        """获取产品市场报告"""
        
        if product_name not in self.product_market:
            return {"error": "产品不存在"}
        
        data = self.product_market[product_name]
        
        # 用户画像
        user_profiles = []
        for resident in self.residents.values():
            if product_name in resident.products_used:
                user_profiles.append(resident.to_dict())
        
        return {
            "product": product_name,
            "total_users": data["total_users"],
            "penetration_rate": round(data["total_users"] / len(self.residents) * 100, 1),
            "adoption_curve": data["adoption_curve"],
            "user_demographics": dict(data["user_demographics"]),
            "sample_users": user_profiles[:10]
        }


# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建城市
    city = CitySystem("PersonaLab Demo City")
    
    # 填充人口
    city.populate_city(100)
    
    print("=== 城市概览 ===")
    print(json.dumps(city.get_city_overview(), indent=2, ensure_ascii=False))
    
    # 引入产品
    product = {
        "name": "效率笔记App",
        "category": "效率工具",
        "price": 99,
        "target_users": ["产品经理", "软件工程师", "学生"]
    }
    
    city.introduce_product(product)
    
    # 模拟传播
    print("\n=== 产品传播模拟 ===")
    result = city.simulate_product_adoption("效率笔记App", days=7)
    print(f"总用户: {result['total_users']}")
    print(f"渗透率: {result['penetration_rate']}%")
    
    print("\n=== 市场报告 ===")
    report = city.get_product_market_report("效率笔记App")
    print(f"用户职业分布: {report['user_demographics']}")
