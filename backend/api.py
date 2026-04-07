"""
PersonaLab API Server
FastAPI 后端服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime
import uvicorn

from agent_generator import AgentGenerator, AgentProfile
from sandbox_engine import SandboxEngine, SimulationConfig, SimulationResult


app = FastAPI(
    title="PersonaLab API",
    description="A2A 产品验证 SaaS - API",
    version="0.1.0"
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


class AgentGenerateRequest(BaseModel):
    count: int = 100
    constraints: Optional[Dict] = None


# ============ API 端点 ============

@app.get("/")
async def root():
    return {
        "name": "PersonaLab API",
        "version": "0.1.0",
        "status": "running"
    }


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


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取单个Agent详情"""
    # Demo: 重新生成
    agent = AgentGenerator.generate_agent()
    return agent.to_dict()


@app.post("/api/simulate")
async def run_simulation(request: SimulationRequest):
    """运行沙盘模拟"""
    
    # 生成Agent
    agents = AgentGenerator.generate_population(request.agent_count)
    
    # 创建配置
    config = SimulationConfig(
        product_name=request.product_name,
        product_description=request.product_description,
        features=[f.dict() for f in request.features],
        virtual_days=request.virtual_days
    )
    
    # 运行模拟
    engine = SandboxEngine(config, agents)
    result = await engine.run()
    
    # 存储
    simulations[result.session_id] = result
    
    return result.to_dict()


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


# ============ 启动 ============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
