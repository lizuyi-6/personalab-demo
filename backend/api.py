"""
PersonaLab API Server v0.3
FastAPI 后端服务 - 增强版 PRD 生成工作流
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime
import uvicorn
import io

from agent_generator import AgentGenerator, AgentProfile
from sandbox_engine import SandboxEngine, SimulationConfig, SimulationResult
from llm_client import llm_router
from prd_parser import PRDParser, DocumentType
from prd_generator import PRDGenerator, GeneratedPRD
from report_generator import ReportGenerator


app = FastAPI(
    title="PersonaLab API",
    description="A2A 产品验证 SaaS - API v0.3",
    version="0.3.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存存储（Demo用）
simulations: Dict[str, SimulationResult] = {}
prd_cache: Dict[str, Dict] = {}
generated_prds: Dict[str, GeneratedPRD] = {}


# ============ 请求模型 ============

class FeatureModel(BaseModel):
    name: str
    complexity: float = 0.5
    solves: List[str] = []


class SimulationRequest(BaseModel):
    product_name: str
    product_description: str
    features: List[FeatureModel]
    agent_count: int = 50
    virtual_days: int = 7
    use_llm: bool = False


class AgentGenerateRequest(BaseModel):
    count: int = 100
    constraints: Optional[Dict] = None


class PRDParseRequest(BaseModel):
    content: str
    doc_type: str = "text"


class PRDGenerateRequest(BaseModel):
    """PRD 生成请求"""
    product_idea: str
    product_name: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None


class PRDConfirmRequest(BaseModel):
    """PRD 确认请求"""
    prd_id: str
    edited_prd: Optional[Dict] = None  # 用户编辑后的 PRD
    agent_count: int = 50
    virtual_days: int = 7


# ============ API 端点 ============

@app.get("/")
async def root():
    return {
        "name": "PersonaLab API",
        "version": "0.3.0",
        "status": "running",
        "features": [
            "OCEAN 人格模型",
            "沙盘推演引擎",
            "PRD 自动生成",  # 新增
            "PRD 文档解析",
            "报告生成",
            "多模型 LLM 路由"
        ]
    }


@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    return {
        "simulations_count": len(simulations),
        "generated_prds_count": len(generated_prds),
        "llm_stats": llm_router.get_stats()
    }


# ============ PRD 生成（新工作流核心） ============

@app.post("/api/prd/generate")
async def generate_prd(request: PRDGenerateRequest):
    """
    根据产品想法生成 PRD 文档
    
    工作流：
    1. 用户输入产品想法
    2. AI 生成完整 PRD
    3. 返回 PRD 供用户确认/修改
    """
    
    prd = PRDGenerator.generate(
        product_idea=request.product_idea,
        product_name=request.product_name,
        industry=request.industry,
        target_audience=request.target_audience
    )
    
    # 生成唯一 ID
    prd_id = f"prd_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(prd) % 10000}"
    
    # 缓存
    generated_prds[prd_id] = prd
    
    return {
        "prd_id": prd_id,
        "prd": prd.to_dict(),
        "markdown": prd.to_markdown(),
        "message": "PRD 已生成，请确认是否符合您的想法"
    }


@app.get("/api/prd/{prd_id}")
async def get_generated_prd(prd_id: str):
    """获取生成的 PRD"""
    if prd_id not in generated_prds:
        raise HTTPException(status_code=404, detail="PRD not found")
    
    prd = generated_prds[prd_id]
    
    return {
        "prd_id": prd_id,
        "prd": prd.to_dict(),
        "markdown": prd.to_markdown()
    }


@app.post("/api/prd/{prd_id}/confirm")
async def confirm_prd(prd_id: str, request: PRDConfirmRequest):
    """
    确认 PRD 并启动沙盘模拟
    
    工作流：
    1. 用户确认/修改 PRD
    2. 启动沙盘模拟
    3. 返回模拟结果
    """
    
    if prd_id not in generated_prds:
        raise HTTPException(status_code=404, detail="PRD not found")
    
    prd = generated_prds[prd_id]
    
    # 如果用户编辑了 PRD，使用编辑版本
    if request.edited_prd:
        # 更新 PRD
        for key, value in request.edited_prd.items():
            if hasattr(prd, key):
                setattr(prd, key, value)
    
    # 转换功能格式
    features = [
        {
            "name": f.get("name", "未命名功能"),
            "complexity": cls._complexity_str_to_float(f.get("complexity", "中等")),
            "solves": []
        }
        for f in prd.core_features
    ]
    
    # 如果没有功能，使用默认
    if not features:
        features = [{"name": "核心功能", "complexity": 0.5, "solves": []}]
    
    # 生成 Agent
    agents = AgentGenerator.generate_population(request.agent_count)
    
    # 创建配置
    config = SimulationConfig(
        product_name=prd.title,
        product_description=prd.product_summary,
        features=features,
        virtual_days=request.virtual_days
    )
    
    # 运行模拟
    engine = SandboxEngine(config, agents)
    result = await engine.run()
    
    # 存储
    simulations[result.session_id] = result
    
    return {
        "prd_id": prd_id,
        "session_id": result.session_id,
        "result": result.to_dict(),
        "message": "模拟完成！"
    }


def _complexity_str_to_float(complexity_str: str) -> float:
    """复杂度字符串转数值"""
    mapping = {
        "低": 0.3,
        "中等": 0.5,
        "高": 0.7,
        "非常高": 0.9
    }
    return mapping.get(complexity_str, 0.5)


@app.put("/api/prd/{prd_id}")
async def update_prd(prd_id: str, updates: Dict):
    """更新 PRD（用户编辑）"""
    if prd_id not in generated_prds:
        raise HTTPException(status_code=404, detail="PRD not found")
    
    prd = generated_prds[prd_id]
    
    # 更新字段
    for key, value in updates.items():
        if hasattr(prd, key):
            setattr(prd, key, value)
    
    return {
        "prd_id": prd_id,
        "prd": prd.to_dict(),
        "message": "PRD 已更新"
    }


# ============ Agent 相关 ============

@app.post("/api/agents/generate")
async def generate_agents(request: AgentGenerateRequest):
    """生成一批拟态用户"""
    agents = AgentGenerator.generate_population(
        count=request.count,
        distribution=request.constraints
    )
    
    return {
        "count": len(agents),
        "agents": [agent.to_dict() for agent in agents]
    }


@app.get("/api/agents/{agent_id}/prompt")
async def get_agent_prompt(agent_id: str):
    """获取 Agent 的模拟 Prompt"""
    agent = AgentGenerator.generate_agent()
    return {
        "agent_id": agent_id,
        "prompt": agent.to_simulation_prompt()
    }


# ============ 旧 PRD 解析（保留兼容） ============

@app.post("/api/prd/parse")
async def parse_prd(request: PRDParseRequest):
    """解析 PRD 文档"""
    
    doc_type_map = {
        "text": DocumentType.TEXT,
        "md": DocumentType.MARKDOWN,
        "markdown": DocumentType.MARKDOWN,
        "pdf": DocumentType.PDF,
        "word": DocumentType.WORD
    }
    
    doc_type = doc_type_map.get(request.doc_type.lower(), DocumentType.TEXT)
    
    parsed = PRDParser.parse(request.content, doc_type)
    
    prd_id = f"prd_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    prd_cache[prd_id] = parsed.to_dict()
    
    return {
        "prd_id": prd_id,
        "parsed": parsed.to_dict()
    }


# ============ 模拟相关 ============

@app.post("/api/simulate")
async def run_simulation(request: SimulationRequest):
    """运行沙盘模拟（直接模式）"""
    
    agents = AgentGenerator.generate_population(request.agent_count)
    
    config = SimulationConfig(
        product_name=request.product_name,
        product_description=request.product_description,
        features=[f.dict() for f in request.features],
        virtual_days=request.virtual_days
    )
    
    engine = SandboxEngine(config, agents)
    result = await engine.run()
    
    simulations[result.session_id] = result
    
    return result.to_dict()


@app.get("/api/simulations")
async def list_simulations():
    """列出所有模拟"""
    return {
        "count": len(simulations),
        "sessions": [
            {
                "session_id": sid,
                "product_name": sim.config.product_name,
                "metrics": sim.metrics
            }
            for sid, sim in simulations.items()
        ]
    }


@app.get("/api/simulations/{session_id}")
async def get_simulation(session_id: str):
    """获取模拟结果"""
    if session_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulations[session_id].to_dict()


@app.get("/api/simulations/{session_id}/actions")
async def get_actions(session_id: str, limit: int = 100):
    """获取模拟行为流"""
    if session_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    result = simulations[session_id]
    actions = result.actions[:limit]
    
    return {
        "total": len(result.actions),
        "actions": [
            {
                "agent_id": a.agent_id,
                "type": a.action_type.value,
                "target": a.target,
                "feedback": a.feedback,
                "timestamp": a.timestamp.isoformat()
            }
            for a in actions
        ]
    }


@app.get("/api/simulations/{session_id}/insights")
async def get_insights(session_id: str):
    """获取洞察报告"""
    if session_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return {
        "session_id": session_id,
        "insights": simulations[session_id].insights,
        "metrics": simulations[session_id].metrics
    }


@app.get("/api/simulations/{session_id}/report")
async def get_full_report(session_id: str):
    """获取完整报告 (Markdown)"""
    if session_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    result = simulations[session_id]
    
    actions = [
        {
            "type": a.action_type.value,
            "feedback": a.feedback
        }
        for a in result.actions
    ]
    
    report = ReportGenerator.generate_full_report(
        session_id=session_id,
        product_name=result.config.product_name,
        metrics=result.metrics,
        insights=result.insights,
        actions=actions
    )
    
    return PlainTextResponse(content=report, media_type="text/markdown")


# ============ LLM 相关 ============

@app.get("/api/llm/status")
async def get_llm_status():
    """获取 LLM 状态"""
    return llm_router.get_stats()


@app.post("/api/llm/test")
async def test_llm(prompt: str, mode: str = "mock"):
    """测试 LLM 调用"""
    result = await llm_router.call(prompt, mode=mode)
    return {
        "prompt": prompt,
        "result": result,
        "mode": mode
    }


# ============ 启动 ============

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║     PersonaLab API v0.3                  ║
    ║     A2A 产品验证沙盘                      ║
    ║                                          ║
    ║     新增：PRD 自动生成工作流              ║
    ╚═══════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
