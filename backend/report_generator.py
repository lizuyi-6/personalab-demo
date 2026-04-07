"""
Report Generator - 洞察报告生成器
生成专业的产品验证报告
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import textwrap


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    level: int = 1
    subsections: List['ReportSection'] = field(default_factory=list)


class ReportGenerator:
    """报告生成器"""
    
    @classmethod
    def generate_full_report(
        cls,
        session_id: str,
        product_name: str,
        metrics: Dict,
        insights: List[str],
        actions: List[Dict],
        agent_profiles: List[Dict] = None
    ) -> str:
        """生成完整报告"""
        
        sections = []
        
        # 1. 执行摘要
        sections.append(cls._generate_executive_summary(
            product_name, metrics, insights
        ))
        
        # 2. 核心指标
        sections.append(cls._generate_metrics_section(metrics))
        
        # 3. 用户行为分析
        sections.append(cls._generate_behavior_analysis(actions))
        
        # 4. 功能热度分析
        sections.append(cls._generate_feature_analysis(actions, metrics))
        
        # 5. 风险警报
        sections.append(cls._generate_risk_alerts(metrics, insights))
        
        # 6. 改进建议
        sections.append(cls._generate_recommendations(metrics, insights))
        
        # 7. 附录：用户反馈采样
        sections.append(cls._generate_feedback_sampling(actions))
        
        return cls._render_markdown_report(
            session_id, product_name, sections
        )
    
    @classmethod
    def _generate_executive_summary(
        cls,
        product_name: str,
        metrics: Dict,
        insights: List[str]
    ) -> ReportSection:
        """生成执行摘要"""
        
        # 判断整体表现
        score = cls._calculate_overall_score(metrics)
        
        if score >= 70:
            verdict = "✅ 产品表现良好，建议进入开发阶段"
            color = "green"
        elif score >= 50:
            verdict = "🟡 产品有潜力，但存在明显问题需优化"
            color = "yellow"
        else:
            verdict = "🔴 产品存在严重问题，建议重新评估核心价值"
            color = "red"
        
        content = f"""
**综合评分**: {score}/100

**验证结论**: {verdict}

**关键发现**:
{chr(10).join(f'- {i}' for i in insights[:5])}

**下一步建议**:
"""
        
        if metrics.get("signup_rate", 0) < 35:
            content += "\n- 优先优化注册流程，降低门槛"
        if metrics.get("retention_rate", 0) < 40:
            content += "\n- 加强核心价值传递，提升用户粘性"
        if metrics.get("nps", 0) < 0:
            content += "\n- 立即排查核心体验问题"
        
        return ReportSection(
            title="📊 执行摘要",
            content=content.strip()
        )
    
    @classmethod
    def _generate_metrics_section(cls, metrics: Dict) -> ReportSection:
        """生成指标章节"""
        
        content = f"""
| 指标 | 数值 | 基准线 | 评价 |
|------|------|--------|------|
| 注册转化率 | {metrics.get('signup_rate', 0)}% | 35% | {cls._rate_metric(metrics.get('signup_rate', 0), 35)} |
| 用户留存率 | {metrics.get('retention_rate', 0)}% | 40% | {cls._rate_metric(metrics.get('retention_rate', 0), 40)} |
| NPS 净推荐值 | {metrics.get('nps', 0)} | 20 | {cls._rate_metric(metrics.get('nps', 0), 20)} |
| 放弃率 | {metrics.get('abandonment_rate', 0)}% | 15% | {cls._rate_metric(15 - metrics.get('abandonment_rate', 0), 0, inverse=True)} |
| 投诉率 | {metrics.get('complaint_rate', 0)}% | 10% | {cls._rate_metric(10 - metrics.get('complaint_rate', 0), 0, inverse=True)} |

**指标解读**:
"""
        
        # 添加解读
        if metrics.get("signup_rate", 0) > 40:
            content += "\n- ✅ 注册转化率高于行业平均，产品价值感知清晰"
        elif metrics.get("signup_rate", 0) < 30:
            content += "\n- ⚠️ 注册转化率偏低，可能存在价值传递不清或门槛过高问题"
        
        if metrics.get("nps", 0) > 30:
            content += "\n- ✅ NPS 表现优秀，用户有强烈推荐意愿"
        elif metrics.get("nps", 0) < 0:
            content += "\n- 🔴 NPS 为负，用户体验存在严重问题"
        
        return ReportSection(
            title="📈 核心指标",
            content=content.strip()
        )
    
    @classmethod
    def _generate_behavior_analysis(cls, actions: List[Dict]) -> ReportSection:
        """生成行为分析"""
        
        if not actions:
            return ReportSection(
                title="👥 用户行为分析",
                content="暂无行为数据"
            )
        
        # 统计行为类型
        action_counts = {}
        for action in actions:
            action_type = action.get("type", "unknown")
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        total = len(actions)
        
        content = f"""
**行为分布** (总计 {total} 次行为):

| 行为类型 | 次数 | 占比 |
|----------|------|------|
"""
        
        for action_type, count in sorted(action_counts.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            content += f"| {action_type} | {count} | {pct:.1f}% |\n"
        
        # 用户路径分析
        content += "\n**典型用户路径**:\n"
        content += "浏览 → 注册 → 核心功能 → (分支: 深度使用/放弃)\n"
        
        return ReportSection(
            title="👥 用户行为分析",
            content=content.strip()
        )
    
    @classmethod
    def _generate_feature_analysis(cls, actions: List[Dict], metrics: Dict) -> ReportSection:
        """生成功能分析"""
        
        feature_usage = metrics.get("feature_usage", {})
        
        if not feature_usage:
            return ReportSection(
                title="🔥 功能热度分析",
                content="暂无功能使用数据"
            )
        
        # 排序
        sorted_features = sorted(feature_usage.items(), key=lambda x: -x[1])
        
        content = "**功能热度排名**:\n\n"
        
        for i, (feature, count) in enumerate(sorted_features, 1):
            if i <= 3:
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            else:
                emoji = f"{i}."
            
            bar = "█" * min(10, count // 5)
            content += f"{emoji} **{feature}**: {count} 次 {bar}\n"
        
        # 热门 vs 冷门
        if sorted_features:
            hot = sorted_features[0][0]
            cold = [f for f, c in sorted_features[-3:] if c < sorted_features[0][1] * 0.3]
            
            content += f"\n**热门功能**: {hot}\n"
            if cold:
                content += f"**冷门功能**: {', '.join(cold)}\n"
        
        return ReportSection(
            title="🔥 功能热度分析",
            content=content.strip()
        )
    
    @classmethod
    def _generate_risk_alerts(cls, metrics: Dict, insights: List[str]) -> ReportSection:
        """生成风险警报"""
        
        risks = []
        
        # 检查各项指标
        if metrics.get("abandonment_rate", 0) > 25:
            risks.append({
                "level": "🔴 高危",
                "issue": "放弃率过高",
                "impact": "用户首次体验极差，可能永久流失",
                "action": "立即排查注册/核心功能体验"
            })
        
        if metrics.get("nps", 0) < -20:
            risks.append({
                "level": "🔴 高危",
                "issue": "NPS 严重为负",
                "impact": "用户不仅不推荐，还会负面传播",
                "action": "重新评估产品核心价值"
            })
        
        if metrics.get("retention_rate", 0) < 30:
            risks.append({
                "level": "🟡 中危",
                "issue": "留存率严重不足",
                "impact": "用户缺乏持续使用动力",
                "action": "加强引导机制和核心价值传递"
            })
        
        if metrics.get("signup_rate", 0) < 25:
            risks.append({
                "level": "🟡 中危",
                "issue": "注册转化过低",
                "impact": "大量潜在用户流失",
                "action": "简化注册流程，降低门槛"
            })
        
        if not risks:
            risks.append({
                "level": "✅ 低危",
                "issue": "未发现严重风险",
                "impact": "产品表现正常",
                "action": "继续监控并优化细节"
            })
        
        content = "| 风险等级 | 问题 | 影响 | 建议行动 |\n"
        content += "|----------|------|------|----------|\n"
        
        for risk in risks:
            content += f"| {risk['level']} | {risk['issue']} | {risk['impact']} | {risk['action']} |\n"
        
        return ReportSection(
            title="⚠️ 风险警报",
            content=content.strip()
        )
    
    @classmethod
    def _generate_recommendations(cls, metrics: Dict, insights: List[str]) -> ReportSection:
        """生成改进建议"""
        
        recommendations = []
        
        # 基于指标生成建议
        if metrics.get("signup_rate", 0) < 35:
            recommendations.append({
                "priority": "P0",
                "area": "注册流程",
                "suggestion": "简化注册步骤，减少必填项，支持一键登录",
                "expected_impact": "预计提升注册率 10-20%"
            })
        
        if metrics.get("retention_rate", 0) < 40:
            recommendations.append({
                "priority": "P0",
                "area": "核心价值",
                "suggestion": "加强新手引导，突出核心价值点，建立使用习惯",
                "expected_impact": "预计提升留存率 15-25%"
            })
        
        if metrics.get("nps", 0) < 20:
            recommendations.append({
                "priority": "P1",
                "area": "用户体验",
                "suggestion": "优化加载速度，简化操作流程，减少摩擦",
                "expected_impact": "预计提升 NPS 10-20 分"
            })
        
        if metrics.get("abandonment_rate", 0) > 15:
            recommendations.append({
                "priority": "P1",
                "area": "首屏体验",
                "suggestion": "优化首次使用体验，快速展示价值，减少等待",
                "expected_impact": "预计降低放弃率 5-10%"
            })
        
        # 通用建议
        recommendations.append({
            "priority": "P2",
            "area": "持续优化",
            "suggestion": "建立 A/B 测试机制，持续迭代优化",
            "expected_impact": "持续提升各项指标"
        })
        
        content = "**优先级排序的改进建议**:\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            content += f"### {i}. [{rec['priority']}] {rec['area']}\n\n"
            content += f"- **建议**: {rec['suggestion']}\n"
            content += f"- **预期效果**: {rec['expected_impact']}\n\n"
        
        return ReportSection(
            title="💡 改进建议",
            content=content.strip()
        )
    
    @classmethod
    def _generate_feedback_sampling(cls, actions: List[Dict]) -> ReportSection:
        """生成反馈采样"""
        
        if not actions:
            return ReportSection(
                title="💬 用户反馈采样",
                content="暂无反馈数据"
            )
        
        # 分类反馈
        positive = []
        negative = []
        neutral = []
        
        for action in actions:
            feedback = action.get("feedback", "")
            if not feedback:
                continue
            
            if any(kw in feedback for kw in ["不错", "好用", "赞", "喜欢", "推荐"]):
                positive.append(feedback)
            elif any(kw in feedback for kw in ["不好", "差", "慢", "复杂", "放弃", "Bug"]):
                negative.append(feedback)
            else:
                neutral.append(feedback)
        
        content = f"**反馈统计**: 👍 {len(positive)} 条好评 | 👎 {len(negative)} 条差评 | 😐 {len(neutral)} 条中立\n\n"
        
        if positive:
            content += "**好评示例**:\n"
            for fb in positive[:3]:
                content += f'- "{fb}"\n'
            content += "\n"
        
        if negative:
            content += "**差评示例**:\n"
            for fb in negative[:3]:
                content += f'- "{fb}"\n'
            content += "\n"
        
        if neutral:
            content += "**中立反馈**:\n"
            for fb in neutral[:3]:
                content += f'- "{fb}"\n'
        
        return ReportSection(
            title="💬 用户反馈采样",
            content=content.strip()
        )
    
    @classmethod
    def _calculate_overall_score(cls, metrics: Dict) -> int:
        """计算综合评分"""
        
        score = 50  # 基础分
        
        # 注册率贡献 (最多 +15)
        signup = metrics.get("signup_rate", 0)
        if signup > 50:
            score += 15
        elif signup > 35:
            score += 10
        elif signup > 25:
            score += 5
        else:
            score -= 5
        
        # 留存率贡献 (最多 +20)
        retention = metrics.get("retention_rate", 0)
        if retention > 60:
            score += 20
        elif retention > 40:
            score += 10
        elif retention > 25:
            score += 5
        else:
            score -= 10
        
        # NPS 贡献 (最多 +15)
        nps = metrics.get("nps", 0)
        if nps > 50:
            score += 15
        elif nps > 20:
            score += 10
        elif nps > 0:
            score += 5
        else:
            score += nps // 5  # 负分扣分
        
        # 放弃率扣分 (最多 -15)
        abandon = metrics.get("abandonment_rate", 0)
        if abandon > 30:
            score -= 15
        elif abandon > 20:
            score -= 10
        elif abandon > 10:
            score -= 5
        
        return max(0, min(100, score))
    
    @classmethod
    def _rate_metric(cls, value: float, baseline: float, inverse: bool = False) -> str:
        """评价指标"""
        if inverse:
            # 越低越好
            if value > baseline:
                return "✅ 优秀"
            elif value > baseline * 0.5:
                return "🟡 一般"
            else:
                return "⚠️ 需改进"
        else:
            # 越高越好
            if value > baseline * 1.3:
                return "✅ 优秀"
            elif value > baseline:
                return "🟢 良好"
            elif value > baseline * 0.7:
                return "🟡 一般"
            else:
                return "⚠️ 需改进"
    
    @classmethod
    def _render_markdown_report(
        cls,
        session_id: str,
        product_name: str,
        sections: List[ReportSection]
    ) -> str:
        """渲染 Markdown 报告"""
        
        report = f"""# PersonaLab 产品验证报告

**产品名称**: {product_name}  
**Session ID**: {session_id}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        for section in sections:
            report += f"## {section.title}\n\n"
            report += section.content
            report += "\n\n---\n\n"
        
        report += """## 📄 附录

本报告由 PersonaLab A2A 产品验证沙盘自动生成。

**技术说明**:
- 基于 OCEAN 五因素人格模型生成 AI 用户
- 引入博弈论约束确保模拟真实性
- 所有数据均为模拟生成，仅供参考

**联系方式**: https://github.com/lizuyi-6/personalab-demo
"""
        
        return report


# ============ 使用示例 ============

if __name__ == "__main__":
    # 测试报告生成
    test_metrics = {
        "signup_rate": 42,
        "retention_rate": 38,
        "nps": 15,
        "abandonment_rate": 18,
        "complaint_rate": 8,
        "feature_usage": {
            "核心笔记": 234,
            "Markdown编辑": 189,
            "AI摘要": 156,
            "团队协作": 45
        }
    }
    
    test_insights = [
        "⚠️ 留存率不足，用户缺乏持续使用的动力",
        "🔥 热门功能：核心笔记",
        "❄️ 冷门功能：团队协作"
    ]
    
    test_actions = [
        {"type": "view", "feedback": "界面不错"},
        {"type": "signup", "feedback": "注册很快"},
        {"type": "complain", "feedback": "加载太慢了"},
        {"type": "praise", "feedback": "这个功能很实用！"},
    ]
    
    report = ReportGenerator.generate_full_report(
        session_id="test_123",
        product_name="效率笔记App",
        metrics=test_metrics,
        insights=test_insights,
        actions=test_actions
    )
    
    print(report)
