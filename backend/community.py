"""
PersonaLab Community - Agent 社区系统
模拟真实的社区生态：发帖、评论、点赞、关注
"""

import random
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import uuid


class ContentType(Enum):
    """内容类型"""
    POST = "post"           # 帖子
    COMMENT = "comment"     # 评论
    REVIEW = "review"       # 评测
    QUESTION = "question"   # 提问
    ANSWER = "answer"       # 回答


class Sentiment(Enum):
    """情感倾向"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class CommunityContent:
    """社区内容"""
    content_id: str
    content_type: ContentType
    author_id: str
    feature: str           # 相关功能
    title: str = ""
    body: str = ""
    sentiment: Sentiment = Sentiment.NEUTRAL
    
    # 互动数据
    likes: int = 0
    dislikes: int = 0
    comments: List[str] = field(default_factory=list)
    shares: int = 0
    views: int = 0
    
    # 时间
    created_at: datetime = field(default_factory=datetime.now)
    
    # 热度分数
    hot_score: float = 0.0
    
    def calculate_hot_score(self) -> float:
        """计算热度分数 (类似 Reddit 算法)"""
        # 时间衰减
        age_hours = (datetime.now() - self.created_at).total_seconds() / 3600
        time_decay = 1 / (1 + age_hours / 12)  # 12小时半衰期
        
        # 互动分数
        engagement = (self.likes * 1 + 
                     self.comments.__len__() * 2 + 
                     self.shares * 3 - 
                     self.dislikes * 0.5)
        
        self.hot_score = engagement * time_decay
        return self.hot_score


@dataclass
class CommunityUser:
    """社区用户"""
    user_id: str
    username: str
    
    # 社交关系
    following: Set[str] = field(default_factory=set)   # 关注的人
    followers: Set[str] = field(default_factory=set)   # 粉丝
    friends: Set[str] = field(default_factory=set)     # 互关好友
    
    # 内容
    posts: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    liked_posts: Set[str] = field(default_factory=set)
    disliked_posts: Set[str] = field(default_factory=set)
    
    # 社区声誉
    reputation: int = 0
    contribution_score: float = 0.0
    
    # 用户等级
    level: str = "新人"  # 新人/活跃/达人/KOL
    
    def update_level(self):
        """更新用户等级"""
        if self.reputation > 100 and len(self.followers) > 50:
            self.level = "KOL"
        elif self.reputation > 50:
            self.level = "达人"
        elif self.reputation > 10:
            self.level = "活跃"
        else:
            self.level = "新人"


@dataclass
class CommunityTopic:
    """话题/标签"""
    topic_name: str
    post_count: int = 0
    follower_count: int = 0
    trending_score: float = 0.0
    related_features: List[str] = field(default_factory=list)


class CommunitySystem:
    """社区系统"""
    
    def __init__(self, community_name: str = "PersonaLab社区"):
        self.community_name = community_name
        
        # 存储
        self.users: Dict[str, CommunityUser] = {}
        self.contents: Dict[str, CommunityContent] = {}
        self.topics: Dict[str, CommunityTopic] = {}
        
        # 索引
        self.feature_posts: Dict[str, List[str]] = defaultdict(list)  # feature -> post_ids
        self.user_feed: Dict[str, List[str]] = defaultdict(list)      # user_id -> post_ids
        
        # 统计
        self.stats = {
            "total_posts": 0,
            "total_comments": 0,
            "total_likes": 0,
            "total_users": 0,
            "active_users_today": set(),
            "hot_topics": []
        }
    
    def initialize_community(self, agent_profiles: List[Dict]):
        """初始化社区，创建用户并建立关系"""
        
        for profile in agent_profiles:
            user_id = profile.get("id", str(uuid.uuid4())[:8])
            username = profile.get("name", f"用户{user_id}")
            
            self.users[user_id] = CommunityUser(
                user_id=user_id,
                username=username
            )
            
            self.stats["total_users"] += 1
        
        # 建立随机社交关系
        user_ids = list(self.users.keys())
        for user_id in user_ids:
            user = self.users[user_id]
            
            # 随机关注 5-20 人
            num_following = random.randint(5, min(20, len(user_ids) - 1))
            following = random.sample([u for u in user_ids if u != user_id], num_following)
            user.following.update(following)
            
            # 更新被关注者的粉丝列表
            for f in following:
                self.users[f].followers.add(user_id)
            
            # 互相关注 = 好友
            user.friends = user.following & user.followers
    
    # ============ 内容发布 ============
    
    def create_post(
        self,
        author_id: str,
        feature: str,
        title: str,
        body: str,
        sentiment: Sentiment = Sentiment.NEUTRAL
    ) -> CommunityContent:
        """发帖"""
        
        content_id = f"post_{uuid.uuid4().hex[:8]}"
        
        post = CommunityContent(
            content_id=content_id,
            content_type=ContentType.POST,
            author_id=author_id,
            feature=feature,
            title=title,
            body=body,
            sentiment=sentiment,
            created_at=datetime.now()
        )
        
        self.contents[content_id] = post
        self.users[author_id].posts.append(content_id)
        self.feature_posts[feature].append(content_id)
        
        # 推送到关注者的 feed
        self._push_to_feed(author_id, content_id)
        
        self.stats["total_posts"] += 1
        self.stats["active_users_today"].add(author_id)
        
        # 更新用户声誉
        self.users[author_id].reputation += 2
        
        return post
    
    def create_comment(
        self,
        author_id: str,
        post_id: str,
        body: str,
        sentiment: Sentiment = Sentiment.NEUTRAL
    ) -> CommunityContent:
        """评论"""
        
        if post_id not in self.contents:
            return None
        
        content_id = f"comment_{uuid.uuid4().hex[:8]}"
        
        comment = CommunityContent(
            content_id=content_id,
            content_type=ContentType.COMMENT,
            author_id=author_id,
            feature=self.contents[post_id].feature,
            body=body,
            sentiment=sentiment,
            created_at=datetime.now()
        )
        
        self.contents[content_id] = comment
        self.contents[post_id].comments.append(content_id)
        self.users[author_id].comments.append(content_id)
        
        self.stats["total_comments"] += 1
        self.stats["active_users_today"].add(author_id)
        
        # 评论增加原作者声誉
        original_author = self.contents[post_id].author_id
        self.users[original_author].reputation += 1
        
        return comment
    
    # ============ 互动功能 ============
    
    def like_post(self, user_id: str, post_id: str) -> bool:
        """点赞"""
        
        if user_id not in self.users or post_id not in self.contents:
            return False
        
        user = self.users[user_id]
        post = self.contents[post_id]
        
        if post_id in user.liked_posts:
            # 取消点赞
            user.liked_posts.remove(post_id)
            post.likes -= 1
            self.users[post.author_id].reputation -= 1
        else:
            # 点赞
            user.liked_posts.add(post_id)
            post.likes += 1
            self.users[post.author_id].reputation += 1
            self.stats["total_likes"] += 1
        
        return True
    
    def share_post(self, user_id: str, post_id: str) -> bool:
        """分享"""
        
        if user_id not in self.users or post_id not in self.contents:
            return False
        
        post = self.contents[post_id]
        post.shares += 1
        
        # 分享给关注者
        self._push_to_feed(user_id, post_id)
        
        # 大幅增加声誉
        self.users[post.author_id].reputation += 5
        
        return True
    
    # ============ 内容生成 ============
    
    def simulate_user_activity(
        self,
        user_id: str,
        features: List[str],
        mood: float,  # -1 到 1
        agent_profile: Dict
    ) -> List[CommunityContent]:
        """模拟用户在社区的活动"""
        
        activities = []
        user = self.users.get(user_id)
        if not user:
            return activities
        
        # 决定活动类型
        activity_roll = random.random()
        
        if activity_roll < 0.3:
            # 30% 概率发帖
            post = self._generate_post(user_id, features, mood, agent_profile)
            if post:
                activities.append(post)
        
        elif activity_roll < 0.6:
            # 30% 概率评论
            comment = self._generate_comment(user_id, mood, agent_profile)
            if comment:
                activities.append(comment)
        
        elif activity_roll < 0.8:
            # 20% 概率浏览+点赞
            self._browse_and_like(user_id, mood)
        
        # 更新用户等级
        user.update_level()
        
        return activities
    
    def _generate_post(
        self,
        user_id: str,
        features: List[str],
        mood: float,
        agent_profile: Dict
    ) -> Optional[CommunityContent]:
        """生成帖子"""
        
        feature = random.choice(features) if features else "产品"
        
        # 根据心情生成内容
        if mood > 0.3:
            sentiment = Sentiment.POSITIVE
            templates = [
                (f"用了{feature}，真香！", "推荐大家试试，解决了我很多问题"),
                (f"{feature}体验不错", "比预期的好用，特别是响应速度"),
                (f"发现一个宝藏功能：{feature}", "太好用了，必须分享给大家"),
            ]
        elif mood < -0.3:
            sentiment = Sentiment.NEGATIVE
            templates = [
                (f"{feature}是什么鬼？", "完全搞不懂怎么用，设计太烂"),
                (f"避雷！{feature}有严重Bug", "用了直接崩溃，数据都没了"),
                (f"对{feature}很失望", "期待了很久，结果是个半成品"),
            ]
        else:
            sentiment = Sentiment.NEUTRAL
            templates = [
                (f"关于{feature}的一些想法", "用了一段时间，有优点也有不足"),
                (f"大家怎么看待{feature}？", "想听听其他用户的意见"),
            ]
        
        title, body = random.choice(templates)
        
        # 性格影响
        personality = agent_profile.get("personality", {})
        if personality.get("agreeableness", 0.5) < 0.3:
            # 低宜人性，内容更尖锐
            body += " (说实话)"
        if personality.get("extraversion", 0.5) > 0.7:
            # 高外向性，更爱分享
            body += " 欢迎大家讨论！"
        
        return self.create_post(user_id, feature, title, body, sentiment)
    
    def _generate_comment(
        self,
        user_id: str,
        mood: float,
        agent_profile: Dict
    ) -> Optional[CommunityContent]:
        """生成评论"""
        
        # 找一个帖子评论
        if not self.contents:
            return None
        
        posts = [c for c in self.contents.values() 
                if c.content_type == ContentType.POST]
        if not posts:
            return None
        
        post = random.choice(posts)
        
        # 生成评论内容
        if mood > 0.3:
            templates = [
                "同感！我也觉得不错",
                "确实好用，推荐",
                "博主说出了我的心声",
            ]
            sentiment = Sentiment.POSITIVE
        elif mood < -0.3:
            templates = [
                "我也遇到了同样的问题",
                "避坑+1",
                "官方什么时候能修复？",
            ]
            sentiment = Sentiment.NEGATIVE
        else:
            templates = [
                "有道理",
                "学习了",
                "观望中",
            ]
            sentiment = Sentiment.NEUTRAL
        
        body = random.choice(templates)
        
        return self.create_comment(user_id, post.content_id, body, sentiment)
    
    def _browse_and_like(self, user_id: str, mood: float):
        """浏览并点赞"""
        
        # 获取用户的 feed
        feed = self.user_feed.get(user_id, [])
        if not feed:
            # 随机浏览一些帖子
            feed = list(self.contents.keys())[:10]
        
        for post_id in feed[:5]:
            if post_id not in self.contents:
                continue
            
            post = self.contents[post_id]
            post.views += 1
            
            # 根据情感匹配决定是否点赞
            if mood > 0.3 and post.sentiment == Sentiment.POSITIVE:
                if random.random() < 0.6:
                    self.like_post(user_id, post_id)
            elif mood < -0.3 and post.sentiment == Sentiment.NEGATIVE:
                if random.random() < 0.4:
                    self.like_post(user_id, post_id)
    
    def _push_to_feed(self, author_id: str, content_id: str):
        """推送到关注者的 feed"""
        
        author = self.users.get(author_id)
        if not author:
            return
        
        # 推送给粉丝
        for follower_id in author.followers:
            self.user_feed[follower_id].insert(0, content_id)
            # 保持 feed 不超过 100 条
            if len(self.user_feed[follower_id]) > 100:
                self.user_feed[follower_id] = self.user_feed[follower_id][:100]
    
    # ============ 数据分析 ============
    
    def get_hot_posts(self, limit: int = 10) -> List[CommunityContent]:
        """获取热门帖子"""
        
        posts = [c for c in self.contents.values() 
                if c.content_type == ContentType.POST]
        
        # 计算热度
        for post in posts:
            post.calculate_hot_score()
        
        # 排序
        sorted_posts = sorted(posts, key=lambda p: -p.hot_score)
        
        return sorted_posts[:limit]
    
    def get_feature_sentiment(self, feature: str) -> Dict:
        """获取功能情感分析"""
        
        posts = [self.contents[pid] for pid in self.feature_posts.get(feature, [])
                if pid in self.contents]
        
        if not posts:
            return {"feature": feature, "sentiment": "unknown", "score": 0}
        
        positive = sum(1 for p in posts if p.sentiment == Sentiment.POSITIVE)
        negative = sum(1 for p in posts if p.sentiment == Sentiment.NEGATIVE)
        neutral = sum(1 for p in posts if p.sentiment == Sentiment.NEUTRAL)
        
        total = len(posts)
        score = (positive - negative) / total if total > 0 else 0
        
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "feature": feature,
            "sentiment": sentiment,
            "score": round(score, 2),
            "posts_count": total,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral
        }
    
    def get_trending_topics(self) -> List[Dict]:
        """获取热门话题"""
        
        trending = []
        
        for feature, post_ids in self.feature_posts.items():
            sentiment_data = self.get_feature_sentiment(feature)
            
            # 热度 = 帖子数 × 情感强度
            heat = len(post_ids) * (1 + abs(sentiment_data["score"]))
            
            trending.append({
                "feature": feature,
                "heat": round(heat, 1),
                "posts": len(post_ids),
                "sentiment": sentiment_data["sentiment"]
            })
        
        return sorted(trending, key=lambda x: -x["heat"])[:10]
    
    def get_community_stats(self) -> Dict:
        """获取社区统计"""
        
        # 更新用户等级分布
        level_dist = defaultdict(int)
        for user in self.users.values():
            level_dist[user.level] += 1
        
        return {
            "community_name": self.community_name,
            "total_users": self.stats["total_users"],
            "active_users_today": len(self.stats["active_users_today"]),
            "total_posts": self.stats["total_posts"],
            "total_comments": self.stats["total_comments"],
            "total_likes": self.stats["total_likes"],
            "level_distribution": dict(level_dist),
            "trending_features": self.get_trending_topics()[:5]
        }
    
    def get_user_profile(self, user_id: str) -> Dict:
        """获取用户社区画像"""
        
        user = self.users.get(user_id)
        if not user:
            return {}
        
        return {
            "user_id": user_id,
            "username": user.username,
            "level": user.level,
            "reputation": user.reputation,
            "following_count": len(user.following),
            "followers_count": len(user.followers),
            "friends_count": len(user.friends),
            "posts_count": len(user.posts),
            "comments_count": len(user.comments),
            "contribution_score": user.contribution_score
        }


# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建社区
    community = CommunitySystem("PersonaLab Demo社区")
    
    # 初始化用户
    agent_profiles = [
        {"id": f"agent_{i}", "name": f"用户{i}"}
        for i in range(50)
    ]
    community.initialize_community(agent_profiles)
    
    print("=== 社区初始化 ===")
    print(community.get_community_stats())
    
    # 模拟活动
    print("\n=== 模拟社区活动 ===")
    for i in range(20):
        user_id = f"agent_{random.randint(0, 49)}"
        community.simulate_user_activity(
            user_id,
            ["核心功能", "AI摘要", "团队协作"],
            random.uniform(-0.5, 0.8),
            {}
        )
    
    print(community.get_community_stats())
    
    print("\n=== 热门帖子 ===")
    for post in community.get_hot_posts(5):
        print(f"  [{post.sentiment.value}] {post.title} (热度: {post.hot_score:.1f})")
    
    print("\n=== 功能情感分析 ===")
    for feature in ["核心功能", "AI摘要"]:
        print(f"  {community.get_feature_sentiment(feature)}")
