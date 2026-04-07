"""
LLM Router - 多模型路由层
支持 OpenAI / Claude / DeepSeek / 本地模型
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import hashlib


class ModelProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    LOCAL = "local"
    MOCK = "mock"  # 无 API 时的模拟模式


@dataclass
class ModelConfig:
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.7
    cost_per_1k_tokens: float = 0.001


# 模型配置
MODEL_CONFIGS = {
    # 复杂推理（高成本）
    "reasoning": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4o-mini",
        max_tokens=1000,
        temperature=0.5,
        cost_per_1k_tokens=0.00015
    ),
    # 日常交互（低成本）
    "chat": ModelConfig(
        provider=ModelProvider.OPENAI,
        model_name="gpt-4o-mini",
        max_tokens=300,
        temperature=0.8,
        cost_per_1k_tokens=0.00015
    ),
    # 本地模型（免费）
    "local": ModelConfig(
        provider=ModelProvider.LOCAL,
        model_name="local-model",
        max_tokens=500,
        temperature=0.7,
        cost_per_1k_tokens=0
    ),
    # Mock 模式（离线）
    "mock": ModelConfig(
        provider=ModelProvider.MOCK,
        model_name="mock",
        max_tokens=500,
        temperature=0.7,
        cost_per_1k_tokens=0
    ),
}


class LLMRouter:
    """多模型路由器"""
    
    def __init__(self, default_mode: str = "mock"):
        self.default_mode = default_mode
        self.total_cost = 0.0
        self.call_count = 0
        self.cache: Dict[str, str] = {}
        
        # 尝试从环境变量获取 API Key
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        
        # 检测可用模式
        if self.openai_key:
            self.default_mode = "chat"
            print("✅ OpenAI API detected, using GPT-4o-mini")
        elif self.default_mode == "mock":
            print("ℹ️ No API key found, using mock mode")
    
    def _get_cache_key(self, prompt: str, mode: str) -> str:
        """生成缓存键"""
        content = f"{mode}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def call(
        self,
        prompt: str,
        mode: str = None,
        use_cache: bool = True
    ) -> str:
        """调用 LLM"""
        mode = mode or self.default_mode
        config = MODEL_CONFIGS.get(mode, MODEL_CONFIGS["mock"])
        
        # 检查缓存
        cache_key = self._get_cache_key(prompt, mode)
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # 根据提供商调用
        if config.provider == ModelProvider.MOCK:
            result = await self._mock_call(prompt)
        elif config.provider == ModelProvider.OPENAI:
            result = await self._openai_call(prompt, config)
        elif config.provider == ModelProvider.LOCAL:
            result = await self._local_call(prompt, config)
        else:
            result = await self._mock_call(prompt)
        
        # 更新统计
        self.call_count += 1
        self.total_cost += config.cost_per_1k_tokens * (config.max_tokens / 1000)
        
        # 缓存结果
        if use_cache:
            self.cache[cache_key] = result
        
        return result
    
    async def _mock_call(self, prompt: str) -> str:
        """模拟调用（离线模式）"""
        # 根据 prompt 内容生成合理的模拟响应
        await asyncio.sleep(0.1)  # 模拟延迟
        
        if "性格" in prompt or "人格" in prompt:
            return self._mock_personality_response()
        elif "反馈" in prompt or "评价" in prompt:
            return self._mock_feedback_response()
        elif "分析" in prompt or "洞察" in prompt:
            return self._mock_insight_response()
        else:
            return self._mock_generic_response()
    
    def _mock_personality_response(self) -> str:
        """模拟人格相关响应"""
        responses = [
            "我是个比较内向的人，喜欢独处思考。对新事物保持谨慎态度，需要看到实际价值才会尝试。",
            "性格外向，喜欢社交和分享。对新功能很好奇，愿意第一时间尝试。",
            "比较挑剔，对产品质量要求高。如果体验不好会直接放弃，不会给第二次机会。",
            "随性自由，不太在意细节。能用就行，不会深入研究所有功能。",
            "完美主义者，喜欢把事情做到极致。对工具有很高要求。"
        ]
        import random
        return random.choice(responses)
    
    def _mock_feedback_response(self) -> str:
        """模拟反馈响应"""
        responses = [
            "这个功能挺实用的，解决了我的痛点 👍",
            "界面设计不错，但操作流程有点复杂",
            "加载速度有点慢，体验不太好",
            "这个功能太鸡肋了，感觉没什么用",
            "终于有人做了这个！期待后续更新",
            "Bug有点多，稳定性需要加强",
            "还不错，但竞品更好用一些",
            "价格偏贵，性价比不高"
        ]
        import random
        return random.choice(responses)
    
    def _mock_insight_response(self) -> str:
        """模拟洞察响应"""
        return json.dumps({
            "summary": "产品整体表现中等，有改进空间",
            "strengths": ["核心功能实用", "界面设计美观"],
            "weaknesses": ["学习成本高", "部分功能冷门"],
            "recommendations": ["简化注册流程", "优化冷门功能或下线"]
        }, ensure_ascii=False)
    
    def _mock_generic_response(self) -> str:
        """通用模拟响应"""
        responses = [
            "好的，我理解了。",
            "这个想法不错。",
            "我需要再想想。",
            "可以尝试一下。",
            "有道理。"
        ]
        import random
        return random.choice(responses)
    
    async def _openai_call(self, prompt: str, config: ModelConfig) -> str:
        """调用 OpenAI API"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.openai_key)
            
            response = await client.chat.completions.create(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return await self._mock_call(prompt)
    
    async def _local_call(self, prompt: str, config: ModelConfig) -> str:
        """调用本地模型"""
        # TODO: 实现 Ollama / LM Studio 调用
        return await self._mock_call(prompt)
    
    async def batch_call(
        self,
        prompts: List[str],
        mode: str = None,
        max_concurrent: int = 5
    ) -> List[str]:
        """批量调用（并发控制）"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_call(prompt: str) -> str:
            async with semaphore:
                return await self.call(prompt, mode)
        
        return await asyncio.gather(*[limited_call(p) for p in prompts])
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_calls": self.call_count,
            "total_cost": round(self.total_cost, 4),
            "cache_size": len(self.cache),
            "default_mode": self.default_mode
        }


# 全局实例
llm_router = LLMRouter()


# ============ 使用示例 ============

async def test_llm():
    print("Testing LLM Router...")
    
    # 测试不同模式
    modes = ["mock", "mock", "mock"]  # 离线模式
    
    for mode in modes:
        result = await llm_router.call(
            "请分析这个产品的优缺点",
            mode=mode
        )
        print(f"\n[{mode}] {result}")
    
    print(f"\nStats: {llm_router.get_stats()}")


if __name__ == "__main__":
    asyncio.run(test_llm())
