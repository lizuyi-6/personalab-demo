"""
PRD Generator - 产品需求文档生成器
根据简短的产品想法生成完整的 PRD
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GeneratedPRD:
    """生成的 PRD 结构"""
    title: str
    version: str = "1.0"
    author: str = "PersonaLab AI"
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    
    # 产品概述
    product_summary: str = ""
    product_vision: str = ""
    
    # 目标用户
    target_users: List[Dict] = field(default_factory=list)
    
    # 核心功能
    core_features: List[Dict] = field(default_factory=list)
    
    # 用户流程
    user_flows: List[Dict] = field(default_factory=list)
    
    # 痛点与解决方案
    pain_points: List[Dict] = field(default_factory=list)
    
    # 成功指标
    success_metrics: List[Dict] = field(default_factory=list)
    
    # 技术要求
    technical_requirements: List[str] = field(default_factory=list)
    
    # 风险评估
    risks: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "version": self.version,
            "author": self.author,
            "date": self.date,
            "product_summary": self.product_summary,
            "product_vision": self.product_vision,
            "target_users": self.target_users,
            "core_features": self.core_features,
            "user_flows": self.user_flows,
            "pain_points": self.pain_points,
            "success_metrics": self.success_metrics,
            "technical_requirements": self.technical_requirements,
            "risks": self.risks
        }
    
    def to_markdown(self) -> str:
        """生成 Markdown 格式的 PRD"""
        md = f"""# {self.title} - 产品需求文档 (PRD)

**版本**: {self.version}  
**作者**: {self.author}  
**日期**: {self.date}

---

## 1. 产品概述

### 1.1 产品简介
{self.product_summary}

### 1.2 产品愿景
{self.product_vision}

---

## 2. 目标用户

| 用户群体 | 描述 | 核心需求 |
|----------|------|----------|
"""
        for user in self.target_users:
            md += f"| {user.get('name', '')} | {user.get('description', '')} | {user.get('needs', '')} |\n"
        
        md += "\n---\n\n## 3. 核心功能\n\n"
        
        for i, feature in enumerate(self.core_features, 1):
            md += f"""### 3.{i} {feature.get('name', '未命名功能')}

**功能描述**: {feature.get('description', '')}

**优先级**: {feature.get('priority', 'P1')}

**复杂度**: {feature.get('complexity', '中等')}

**用户价值**: {feature.get('value', '')}

**使用场景**:
"""
            for scenario in feature.get('scenarios', []):
                md += f"- {scenario}\n"
            md += "\n"
        
        md += "---\n\n## 4. 用户流程\n\n"
        
        for flow in self.user_flows:
            md += f"""### {flow.get('name', '用户流程')}

**触发条件**: {flow.get('trigger', '')}

**流程步骤**:
"""
            for step in flow.get('steps', []):
                md += f"1. {step}\n"
            md += "\n"
        
        md += "---\n\n## 5. 痛点与解决方案\n\n"
        
        md += "| 用户痛点 | 当前解决方案 | 我们的方案 | 优势 |\n"
        md += "|----------|--------------|------------|------|\n"
        for pp in self.pain_points:
            md += f"| {pp.get('pain', '')} | {pp.get('current', '')} | {pp.get('solution', '')} | {pp.get('advantage', '')} |\n"
        
        md += "\n---\n\n## 6. 成功指标\n\n"
        
        md += "| 指标 | 目标值 | 衡量方式 |\n"
        md += "|------|--------|----------|\n"
        for metric in self.success_metrics:
            md += f"| {metric.get('name', '')} | {metric.get('target', '')} | {metric.get('method', '')} |\n"
        
        md += "\n---\n\n## 7. 技术要求\n\n"
        for req in self.technical_requirements:
            md += f"- {req}\n"
        
        md += "\n---\n\n## 8. 风险评估\n\n"
        
        md += "| 风险 | 可能性 | 影响 | 应对策略 |\n"
        md += "|------|--------|------|----------|\n"
        for risk in self.risks:
            md += f"| {risk.get('risk', '')} | {risk.get('probability', '')} | {risk.get('impact', '')} | {risk.get('mitigation', '')} |\n"
        
        md += f"""

---

## 9. 附录

### 9.1 术语表
- **PRD**: Product Requirements Document，产品需求文档
- **MVP**: Minimum Viable Product，最小可行产品
- **NPS**: Net Promoter Score，净推荐值

### 9.2 参考资料
- 竞品分析报告
- 用户调研数据

---

*本文档由 PersonaLab AI 自动生成，请根据实际情况调整*
"""
        return md


class PRDGenerator:
    """PRD 生成器"""
    
    # 行业模板
    INDUSTRY_TEMPLATES = {
        "效率工具": {
            "pain_points": ["时间不够用", "信息碎片化", "任务管理混乱"],
            "features": ["任务清单", "日程管理", "提醒通知", "数据同步"],
            "metrics": ["日活跃用户", "任务完成率", "用户留存率"]
        },
        "社交应用": {
            "pain_points": ["社交圈子窄", "难以找到志同道合的人", "信息过载"],
            "features": ["动态发布", "好友系统", "消息聊天", "兴趣小组"],
            "metrics": ["日活跃用户", "互动率", "分享率"]
        },
        "电商平台": {
            "pain_points": ["商品选择困难", "价格不透明", "物流慢"],
            "features": ["商品搜索", "购物车", "订单管理", "支付系统"],
            "metrics": ["GMV", "转化率", "复购率"]
        },
        "内容平台": {
            "pain_points": ["内容质量参差不齐", "信息获取效率低", "个性化不足"],
            "features": ["内容发布", "推荐系统", "评论互动", "收藏夹"],
            "metrics": ["内容消费量", "互动率", "停留时长"]
        },
        "教育学习": {
            "pain_points": ["学习效率低", "缺乏督促", "资源分散"],
            "features": ["课程管理", "学习进度", "练习测试", "社区讨论"],
            "metrics": ["完课率", "学习时长", "用户满意度"]
        }
    }
    
    # 功能类型模板
    FEATURE_TEMPLATES = {
        "核心功能": {"priority": "P0", "complexity": "中等"},
        "基础功能": {"priority": "P1", "complexity": "低"},
        "高级功能": {"priority": "P2", "complexity": "高"},
        "增值功能": {"priority": "P3", "complexity": "中等"}
    }
    
    @classmethod
    def generate(
        cls,
        product_idea: str,
        product_name: Optional[str] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> GeneratedPRD:
        """根据产品想法生成 PRD"""
        
        # 解析产品想法
        idea_info = cls._parse_idea(product_idea)
        
        # 确定产品名称
        title = product_name or idea_info.get("name", "未命名产品")
        
        # 确定行业
        detected_industry = industry or cls._detect_industry(product_idea)
        template = cls.INDUSTRY_TEMPLATES.get(detected_industry, {})
        
        # 生成 PRD
        prd = GeneratedPRD(title=title)
        
        # 生成产品概述
        prd.product_summary = cls._generate_summary(product_idea, idea_info)
        prd.product_vision = cls._generate_vision(product_idea, idea_info)
        
        # 生成目标用户
        prd.target_users = cls._generate_target_users(
            product_idea, target_audience, template
        )
        
        # 生成核心功能
        prd.core_features = cls._generate_features(
            product_idea, idea_info, template
        )
        
        # 生成用户流程
        prd.user_flows = cls._generate_user_flows(prd.core_features)
        
        # 生成痛点与解决方案
        prd.pain_points = cls._generate_pain_points(
            product_idea, prd.target_users, template
        )
        
        # 生成成功指标
        prd.success_metrics = cls._generate_success_metrics(template)
        
        # 生成技术要求
        prd.technical_requirements = cls._generate_tech_requirements(prd.core_features)
        
        # 生成风险评估
        prd.risks = cls._generate_risks(product_idea, prd.core_features)
        
        return prd
    
    @classmethod
    def _parse_idea(cls, idea: str) -> Dict:
        """解析产品想法"""
        info = {
            "name": "",
            "type": "",
            "keywords": [],
            "core_value": ""
        }
        
        # 提取关键词
        keywords_map = {
            "效率": "效率工具",
            "笔记": "效率工具",
            "社交": "社交应用",
            "聊天": "社交应用",
            "购物": "电商平台",
            "电商": "电商平台",
            "内容": "内容平台",
            "视频": "内容平台",
            "学习": "教育学习",
            "教育": "教育学习",
            "课程": "教育学习"
        }
        
        for keyword, product_type in keywords_map.items():
            if keyword in idea:
                info["keywords"].append(keyword)
                if not info["type"]:
                    info["type"] = product_type
        
        # 提取可能的名称
        lines = idea.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            if len(first_line) < 20:
                info["name"] = first_line.replace("我想做一个", "").replace("做一个", "")
        
        # 核心价值
        if "帮助" in idea:
            idx = idea.index("帮助")
            info["core_value"] = idea[idx:idx+30]
        elif "解决" in idea:
            idx = idea.index("解决")
            info["core_value"] = idea[idx:idx+30]
        
        return info
    
    @classmethod
    def _detect_industry(cls, idea: str) -> str:
        """检测行业"""
        for industry, template in cls.INDUSTRY_TEMPLATES.items():
            for pain in template["pain_points"]:
                if pain in idea:
                    return industry
            for feature in template["features"]:
                if feature in idea:
                    return industry
        
        # 默认返回效率工具
        return "效率工具"
    
    @classmethod
    def _generate_summary(cls, idea: str, idea_info: Dict) -> str:
        """生成产品简介"""
        product_type = idea_info.get("type", "应用")
        keywords = idea_info.get("keywords", [])
        
        summary = f"一款{product_type}类产品，"
        
        if keywords:
            summary += f"专注于{'+'.join(keywords)}领域。"
        
        if idea_info.get("core_value"):
            summary += idea_info["core_value"]
        else:
            summary += "旨在为用户提供便捷、高效的服务体验。"
        
        return summary
    
    @classmethod
    def _generate_vision(cls, idea: str, idea_info: Dict) -> str:
        """生成产品愿景"""
        visions = [
            "成为用户日常生活中不可或缺的工具，提升工作效率和生活质量。",
            "打造最懂用户的产品，让每一次使用都带来价值。",
            "用科技的力量，解决用户最真实的痛点。",
            "构建连接人与信息的桥梁，让世界变得更简单。"
        ]
        
        import random
        return random.choice(visions)
    
    @classmethod
    def _generate_target_users(
        cls,
        idea: str,
        target_audience: Optional[str],
        template: Dict
    ) -> List[Dict]:
        """生成目标用户"""
        users = []
        
        # 基于模板生成
        user_types = [
            ("核心用户", "25-35岁，注重效率，有一定消费能力"),
            ("次要用户", "18-25岁，追求新鲜感，时间充裕"),
            ("潜在用户", "35-45岁，对新技术有好奇心")
        ]
        
        for name, desc in user_types[:2]:
            users.append({
                "name": name,
                "description": desc,
                "needs": "快速解决问题，提升效率" if "效率" in desc else "有趣好玩，社交分享"
            })
        
        return users
    
    @classmethod
    def _generate_features(
        cls,
        idea: str,
        idea_info: Dict,
        template: Dict
    ) -> List[Dict]:
        """生成核心功能"""
        features = []
        
        # 从模板获取基础功能
        base_features = template.get("features", ["核心功能"])
        
        # 功能描述模板
        feature_descs = {
            "任务清单": "用户可以创建、编辑、删除任务，支持分类和标签",
            "日程管理": "日历视图展示任务，支持提醒和重复设置",
            "提醒通知": "支持多种提醒方式，确保用户不遗漏重要事项",
            "数据同步": "跨设备数据同步，随时随地访问",
            "动态发布": "发布图文、视频内容，支持话题标签",
            "好友系统": "关注/粉丝机制，查看好友动态",
            "消息聊天": "实时聊天，支持文字、图片、语音",
            "兴趣小组": "基于兴趣创建小组，话题讨论",
            "商品搜索": "关键词搜索，筛选排序",
            "购物车": "添加商品，批量结算",
            "订单管理": "订单查询，物流跟踪",
            "支付系统": "多种支付方式，安全便捷",
            "内容发布": "发布文章、视频等内容",
            "推荐系统": "个性化推荐，千人千面",
            "评论互动": "点赞、评论、转发",
            "收藏夹": "收藏感兴趣的内容",
            "课程管理": "课程列表，学习进度",
            "学习进度": "可视化展示学习状态",
            "练习测试": "随堂测验，知识巩固",
            "社区讨论": "学员交流，答疑解惑"
        }
        
        for i, feature_name in enumerate(base_features[:5]):
            priority = "P0" if i == 0 else "P1" if i < 3 else "P2"
            
            features.append({
                "name": feature_name,
                "description": feature_descs.get(feature_name, f"{feature_name}功能，提供核心服务"),
                "priority": priority,
                "complexity": "高" if i == 0 else "中等" if i < 3 else "低",
                "value": f"解决用户在{feature_name}方面的需求",
                "scenarios": [
                    f"场景1: 用户需要{feature_name}",
                    f"场景2: 用户希望快速完成{feature_name}"
                ]
            })
        
        return features
    
    @classmethod
    def _generate_user_flows(cls, features: List[Dict]) -> List[Dict]:
        """生成用户流程"""
        flows = []
        
        # 注册流程
        flows.append({
            "name": "用户注册/登录流程",
            "trigger": "新用户首次使用",
            "steps": [
                "打开应用，进入欢迎页",
                "选择注册方式（手机/邮箱/第三方）",
                "填写基本信息",
                "完成验证",
                "进入主页"
            ]
        })
        
        # 核心功能流程
        if features:
            first_feature = features[0]["name"]
            flows.append({
                "name": f"{first_feature}使用流程",
                "trigger": f"用户需要使用{first_feature}",
                "steps": [
                    "点击进入功能页面",
                    "查看/操作内容",
                    "保存/提交",
                    "查看结果"
                ]
            })
        
        return flows
    
    @classmethod
    def _generate_pain_points(
        cls,
        idea: str,
        target_users: List[Dict],
        template: Dict
    ) -> List[Dict]:
        """生成痛点与解决方案"""
        pain_points = []
        
        base_pains = template.get("pain_points", ["用户体验差", "功能不完善", "价格不合理"])
        
        for pain in base_pains[:3]:
            pain_points.append({
                "pain": pain,
                "current": "现有方案体验一般",
                "solution": "我们提供更好的体验",
                "advantage": "更便捷、更智能、更人性化"
            })
        
        return pain_points
    
    @classmethod
    def _generate_success_metrics(cls, template: Dict) -> List[Dict]:
        """生成成功指标"""
        metrics = [
            {"name": "日活跃用户 (DAU)", "target": "10,000+", "method": "统计每日登录用户数"},
            {"name": "用户留存率 (次日)", "target": "40%+", "method": "统计次日回访用户比例"},
            {"name": "用户留存率 (7日)", "target": "20%+", "method": "统计7日后仍活跃用户比例"},
            {"name": "NPS 净推荐值", "target": "30+", "method": "用户调研问卷"},
            {"name": "用户满意度", "target": "4.0/5.0+", "method": "应用商店评分"}
        ]
        
        return metrics
    
    @classmethod
    def _generate_tech_requirements(cls, features: List[Dict]) -> List[str]:
        """生成技术要求"""
        base_reqs = [
            "支持 iOS 14+ / Android 10+ 系统",
            "响应时间 < 2秒",
            "支持高并发访问",
            "数据加密存储，符合隐私保护要求",
            "支持离线模式（部分功能）"
        ]
        
        return base_reqs
    
    @classmethod
    def _generate_risks(cls, idea: str, features: List[Dict]) -> List[Dict]:
        """生成风险评估"""
        risks = [
            {
                "risk": "用户接受度不及预期",
                "probability": "中",
                "impact": "高",
                "mitigation": "充分调研，快速迭代"
            },
            {
                "risk": "竞品抢占市场",
                "probability": "高",
                "impact": "中",
                "mitigation": "差异化定位，快速上线"
            },
            {
                "risk": "技术实现难度大",
                "probability": "中",
                "impact": "中",
                "mitigation": "MVP 优先，逐步完善"
            }
        ]
        
        return risks


# ============ 使用示例 ============

if __name__ == "__main__":
    # 测试 PRD 生成
    idea = """
    我想做一个效率笔记App，帮助用户记录和管理日常笔记，
    支持Markdown编辑，可以同步到云端，还有AI智能摘要功能
    """
    
    prd = PRDGenerator.generate(idea)
    
    print(prd.to_markdown())
    
    print("\n" + "="*50)
    print("JSON 格式:")
    print(json.dumps(prd.to_dict(), indent=2, ensure_ascii=False))
