"""
PRD Parser - 产品需求文档解析器
支持 PDF / Word / Markdown / 纯文本
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DocumentType(Enum):
    PDF = "pdf"
    WORD = "word"
    MARKDOWN = "md"
    TEXT = "text"
    URL = "url"


@dataclass
class ParsedPRD:
    """解析后的 PRD 结构"""
    title: str
    summary: str
    target_users: List[str] = field(default_factory=list)
    core_features: List[Dict] = field(default_factory=list)
    user_flows: List[Dict] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    raw_content: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "summary": self.summary,
            "target_users": self.target_users,
            "core_features": self.core_features,
            "user_flows": self.user_flows,
            "pain_points": self.pain_points,
            "success_metrics": self.success_metrics
        }


class PRDParser:
    """PRD 解析器"""
    
    # 关键词模式
    FEATURE_PATTERNS = [
        r"功能[一二三四五六七八九十\d]*[：:]\s*(.+)",
        r"核心功能[：:]\s*(.+)",
        r"主要功能[：:]\s*(.+)",
        r"[-•]\s*(.+?)(?:\n|$)",
    ]
    
    USER_PATTERNS = [
        r"目标用户[：:]\s*(.+)",
        r"用户画像[：:]\s*(.+)",
        r"面向[：:]\s*(.+)",
    ]
    
    PAIN_POINT_PATTERNS = [
        r"痛点[：:]\s*(.+)",
        r"用户痛点[：:]\s*(.+)",
        r"解决问题[：:]\s*(.+)",
    ]
    
    @classmethod
    def parse(cls, content: str, doc_type: DocumentType = DocumentType.TEXT) -> ParsedPRD:
        """解析 PRD 文档"""
        
        if doc_type == DocumentType.MARKDOWN:
            return cls._parse_markdown(content)
        elif doc_type == DocumentType.PDF:
            return cls._parse_pdf(content)
        elif doc_type == DocumentType.WORD:
            return cls._parse_word(content)
        else:
            return cls._parse_text(content)
    
    @classmethod
    def _parse_text(cls, content: str) -> ParsedPRD:
        """解析纯文本"""
        
        # 提取标题
        title = cls._extract_title(content)
        
        # 提取摘要
        summary = cls._extract_summary(content)
        
        # 提取目标用户
        target_users = cls._extract_by_patterns(content, cls.USER_PATTERNS)
        
        # 提取核心功能
        core_features = cls._extract_features(content)
        
        # 提取痛点
        pain_points = cls._extract_by_patterns(content, cls.PAIN_POINT_PATTERNS)
        
        return ParsedPRD(
            title=title,
            summary=summary,
            target_users=target_users,
            core_features=core_features,
            pain_points=pain_points,
            raw_content=content
        )
    
    @classmethod
    def _parse_markdown(cls, content: str) -> ParsedPRD:
        """解析 Markdown"""
        
        # 提取标题 (第一个 # 标题)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else "未命名产品"
        
        # 提取各部分
        sections = cls._split_markdown_sections(content)
        
        # 解析功能部分
        core_features = []
        if "功能" in sections:
            core_features = cls._parse_feature_list(sections["功能"])
        
        # 解析用户部分
        target_users = []
        if "用户" in sections:
            target_users = cls._parse_user_list(sections["用户"])
        
        # 解析痛点
        pain_points = []
        if "痛点" in sections or "问题" in sections:
            pain_text = sections.get("痛点", sections.get("问题", ""))
            pain_points = cls._parse_list_items(pain_text)
        
        # 提取摘要
        summary = cls._extract_summary(content)
        
        return ParsedPRD(
            title=title,
            summary=summary,
            target_users=target_users,
            core_features=core_features,
            pain_points=pain_points,
            raw_content=content
        )
    
    @classmethod
    def _parse_pdf(cls, content: str) -> ParsedPRD:
        """解析 PDF 内容（纯文本提取后）"""
        # PDF 提取的文本通常格式较差，使用更宽松的解析
        return cls._parse_text(content)
    
    @classmethod
    def _parse_word(cls, content: str) -> ParsedPRD:
        """解析 Word 内容"""
        return cls._parse_text(content)
    
    @classmethod
    def _extract_title(cls, content: str) -> str:
        """提取标题"""
        lines = content.strip().split("\n")
        for line in lines[:5]:  # 只看前5行
            line = line.strip()
            if line and len(line) < 50:
                # 可能是标题
                if not any(kw in line for kw in ["功能", "用户", "需求", "版本"]):
                    return line
        return "未命名产品"
    
    @classmethod
    def _extract_summary(cls, content: str) -> str:
        """提取摘要"""
        # 查找摘要相关段落
        patterns = [
            r"摘要[：:]\s*(.+?)(?:\n\n|\n#|$)",
            r"简介[：:]\s*(.+?)(?:\n\n|\n#|$)",
            r"概述[：:]\s*(.+?)(?:\n\n|\n#|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()[:500]
        
        # 使用第一段作为摘要
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if paragraphs:
            return paragraphs[0][:500]
        
        return ""
    
    @classmethod
    def _extract_by_patterns(cls, content: str, patterns: List[str]) -> List[str]:
        """根据模式提取内容"""
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # 清理和分割
                items = re.split(r"[，,、；;]", match)
                results.extend([item.strip() for item in items if item.strip()])
        return list(set(results))[:10]  # 去重，最多10个
    
    @classmethod
    def _extract_features(cls, content: str) -> List[Dict]:
        """提取功能列表"""
        features = []
        
        # 尝试不同的格式
        # 格式1: 功能1：xxx
        pattern1 = r"功能\s*(\d*)[：:]\s*(.+?)(?=功能\d|核心功能|主要功能|$)"
        matches = re.findall(pattern1, content, re.DOTALL)
        for _, desc in matches:
            features.append({
                "name": desc.split("\n")[0].strip()[:50],
                "description": desc.strip()[:200],
                "complexity": cls._estimate_complexity(desc)
            })
        
        # 格式2: 列表形式
        if not features:
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(r"[-•*]\s*.", line):
                    name = re.sub(r"^[-•*]\s*", "", line).strip()[:50]
                    if name and len(name) > 2:
                        features.append({
                            "name": name,
                            "description": "",
                            "complexity": 0.5
                        })
        
        return features[:20]  # 最多20个功能
    
    @classmethod
    def _estimate_complexity(cls, description: str) -> float:
        """估算功能复杂度"""
        complexity_keywords = {
            "简单": 0.2,
            "基础": 0.3,
            "中等": 0.5,
            "复杂": 0.7,
            "高级": 0.8,
            "智能": 0.7,
            "AI": 0.8,
            "实时": 0.6,
            "协作": 0.6,
            "推荐": 0.7,
            "分析": 0.6,
            "可视化": 0.5,
        }
        
        score = 0.5  # 默认中等
        
        for keyword, weight in complexity_keywords.items():
            if keyword in description:
                score = max(score, weight)
        
        return score
    
    @classmethod
    def _split_markdown_sections(cls, content: str) -> Dict[str, str]:
        """分割 Markdown 章节"""
        sections = {}
        
        # 匹配二级标题
        pattern = r"##\s+(.+?)\n(.+?)(?=##|$)"
        matches = re.findall(pattern, content, re.DOTALL)
        
        for title, body in matches:
            sections[title.strip()] = body.strip()
        
        return sections
    
    @classmethod
    def _parse_feature_list(cls, content: str) -> List[Dict]:
        """解析功能列表"""
        features = []
        lines = content.split("\n")
        
        for line in lines:
            line = line.strip()
            # 匹配 "- 功能名：描述" 或 "1. 功能名"
            match = re.match(r"[-*\d.]+\s*(.+?)[：:]?\s*(.*)", line)
            if match:
                name = match.group(1).strip()
                desc = match.group(2).strip() if match.group(2) else ""
                
                if name and len(name) > 1:
                    features.append({
                        "name": name[:50],
                        "description": desc[:200],
                        "complexity": cls._estimate_complexity(name + desc)
                    })
        
        return features
    
    @classmethod
    def _parse_user_list(cls, content: str) -> List[str]:
        """解析用户列表"""
        users = []
        lines = content.split("\n")
        
        for line in lines:
            line = line.strip()
            match = re.match(r"[-*\d.]+\s*(.+)", line)
            if match:
                user = match.group(1).strip()
                if user and len(user) > 1:
                    users.append(user)
        
        return users
    
    @classmethod
    def _parse_list_items(cls, content: str) -> List[str]:
        """解析列表项"""
        items = []
        lines = content.split("\n")
        
        for line in lines:
            line = line.strip()
            match = re.match(r"[-*\d.]+\s*(.+)", line)
            if match:
                item = match.group(1).strip()
                if item and len(item) > 1:
                    items.append(item)
        
        return items


# ============ 使用示例 ============

if __name__ == "__main__":
    # 测试解析
    sample_prd = """
# 效率笔记 App 产品需求文档

## 概述
一款面向知识工作者的智能笔记应用，帮助用户高效记录和管理信息。

## 目标用户
- 产品经理
- 程序员
- 设计师
- 学生

## 核心功能
1. 快速笔记：支持文字、图片、语音多种输入方式
2. Markdown 编辑：实时预览，支持代码高亮
3. AI 智能摘要：自动提取关键信息生成摘要
4. 知识图谱：可视化笔记之间的关联关系
5. 团队协作：支持多人实时编辑和评论

## 用户痛点
- 信息碎片化，难以整理
- 检索效率低
- 知识不成体系
"""
    
    parsed = PRDParser.parse(sample_prd, DocumentType.MARKDOWN)
    print(json.dumps(parsed.to_dict(), indent=2, ensure_ascii=False))
