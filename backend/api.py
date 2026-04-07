"""
PersonaLab API Server v0.2
FastAPI 后端服务 - 增强版
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
from report_generator import ReportGenerator


app = FastAPI(
    title="PersonaLab API",
    description="A2A 产品验证 SaaS - API v0.2",
    version="0.2.0"
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
    use_llm: bool = False  # 是否使用真实 LLM


class AgentGenerateRequest(BaseModel):
    count: int = 100
    constraints: Optional[Dict] = None


class PRDParseRequest(BaseModel):
    content: str
    doc_type: str = "text"  # text, md, pdf


# ============ API 端点 ============

@app.get("/")
async def root():
    return {
        "name": "PersonaLab API",
        "version": "0.2.0",
        "status": "running",
        "features": [
            "OCEAN 人格模型",
            "沙盘推演引擎",
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
        "llm_stats": llm_router.get_stats()
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


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取单个Agent详情"""
    agent = AgentGenerator.generate_agent()
    return agent.to_dict()


@app.get("/api/agents/{agent_id}/prompt")
async def get_agent_prompt(agent_id: str):
    """获取 Agent 的模拟 Prompt"""
    agent = AgentGenerator.generate_agent()
    return {
        "agent_id": agent_id,
        "prompt": agent.to_simulation_prompt()
    }


# ============ PRD 解析 ============

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
    
    # 缓存
    prd_id = f"prd_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    prd_cache[prd_id] = parsed.to_dict()
    
    return {
        "prd_id": prd_id,
        "parsed": parsed.to_dict()
    }


@app.post("/api/prd/upload")
async def upload_prd(file: UploadFile = File(...)):
    """上传 PRD 文件"""
    
    content = await file.read()
    
    # 根据文件类型解析
    filename = file.filename.lower()
    
    if filename.endswith('.md'):
        doc_type = DocumentType.MARKDOWN
        text = content.decode('utf-8')
    elif filename.endswith('.txt'):
        doc_type = DocumentType.TEXT
        text = content.decode('utf-8')
    elif filename.endswith('.pdf'):
        doc_type = DocumentType.PDF
        # TODO: 使用 PyPDF2 或 pdfplumber 解析
        text = content.decode('utf-8', errors='ignore')
    else:
        doc_type = DocumentType.TEXT
        text = content.decode('utf-8', errors='ignore')
    
    parsed = PRDParser.parse(text, doc_type)
    
    return {
        "filename": file.filename,
        "parsed": parsed.to_dict()
    }


# ============ 模拟相关 ============

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


@app.post("/api/simulate/from-prd")
async def simulate_from_prd(
    prd_content: str,
    agent_count: int = 50,
    virtual_days: int = 7
):
    """从 PRD 内容直接启动模拟"""
    
    # 解析 PRD
    parsed = PRDParser.parse(prd_content, DocumentType.MARKDOWN)
    
    # 转换功能格式
    features = [
        {
            "name": f["name"],
            "complexity": f.get("complexity", 0.5),
            "solves": []
        }
        for f in parsed.core_features
    ]
    
    # 如果没有解析到功能，使用默认
    if not features:
        features = [{"name": "核心功能", "complexity": 0.5, "solves": []}]
    
    # 生成 Agent
    agents = AgentGenerator.generate_population(agent_count)
    
    # 创建配置
    config = SimulationConfig(
        product_name=parsed.title,
        product_description=parsed.summary,
        features=features,
        virtual_days=virtual_days
    )
    
    # 运行模拟
    engine = SandboxEngine(config, agents)
    result = await engine.run()
    
    # 存储
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
    
    # 转换 actions 格式
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
    ║     PersonaLab API v0.2                  ║
    ║     A2A 产品验证沙盘                      ║
    ╚═══════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
