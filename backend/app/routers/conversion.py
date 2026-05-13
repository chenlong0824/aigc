from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.database import get_db, get_db_session
from app.models.models import ChatSession
from app.services.knowledge_service import chat_with_knowledge
from app.services.llm_service import get_model_provider, set_model_provider

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ModelSwitchRequest(BaseModel):
    provider: str


@router.post("/chat/ask")
async def chat_ask(req: ChatRequest):
    session_id = req.session_id or uuid.uuid4().hex[:12]
    answer = await chat_with_knowledge(session_id, req.message)

    import json
    with get_db_session() as db:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        messages = []
        if session:
            try:
                messages = json.loads(session.messages) if session.messages else []
            except json.JSONDecodeError:
                messages = []
        messages.append({"role": "user", "content": req.message})
        messages.append({"role": "assistant", "content": answer})

        if session:
            session.messages = json.dumps(messages, ensure_ascii=False)
        else:
            session = ChatSession(session_id=session_id, messages=json.dumps(messages, ensure_ascii=False))
            db.add(session)
        db.commit()

    has_booking_intent = any(kw in req.message for kw in ["预订", "买票", "购票", "预约", "订房", "订酒店"])

    return {"success": True, "data": {"session_id": session_id, "answer": answer, "has_booking_intent": has_booking_intent}}


@router.get("/chat/history/{session_id}")
def chat_history(session_id: str):
    import json
    with get_db_session() as db:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            return {"success": True, "data": []}
        try:
            messages = json.loads(session.messages) if session.messages else []
        except json.JSONDecodeError:
            messages = []
        return {"success": True, "data": messages}


@router.get("/chat/model/status")
def get_current_model():
    """
    获取当前使用的AI模型提供商
    """
    current = get_model_provider()
    return {
        "success": True,
        "data": {
            "provider": current,
            "name": "Ollama (本地)" if current == "ollama" else "千问 (云端)",
            "description": "本地模型，响应较慢但无需网络" if current == "ollama" else "云端模型，响应快速但需要网络"
        }
    }


@router.post("/chat/model/switch")
def switch_model(req: ModelSwitchRequest):
    """
    切换AI模型提供商

    Args:
        provider: 模型提供商，"ollama" 或 "qwen"
    """
    if req.provider not in ["ollama", "qwen"]:
        return {
            "success": False,
            "error": "无效的模型提供商，可选值：ollama (本地) 或 qwen (云端)"
        }

    success = set_model_provider(req.provider)
    if success:
        return {
            "success": True,
            "data": {
                "provider": req.provider,
                "name": "Ollama (本地)" if req.provider == "ollama" else "千问 (云端)",
                "message": "已切换到本地模型，响应较慢但无需网络" if req.provider == "ollama" else "已切换到云端模型，响应快速但需要网络"
            }
        }
    else:
        return {
            "success": False,
            "error": "切换失败"
        }


@router.get("/analytics/funnel")
def analytics_funnel():
    return {"success": True, "data": {"stages": [{"name": "曝光", "value": 1285600}, {"name": "点击", "value": 385680}, {"name": "互动", "value": 89500}, {"name": "咨询", "value": 25600}, {"name": "预订", "value": 5200}, {"name": "核销", "value": 4100}], "conversion_rate": "0.32%"}}


@router.get("/analytics/attribution")
def analytics_attribution():
    return {"success": True, "data": {"models": [{"name": "首次触达", "channels": [{"channel": "抖音", "contribution": 45.2}, {"channel": "小红书", "contribution": 22.8}, {"channel": "视频号", "contribution": 18.5}, {"channel": "微信", "contribution": 13.5}]}, {"name": "末次触达", "channels": [{"channel": "抖音", "contribution": 38.5}, {"channel": "小红书", "contribution": 28.2}, {"channel": "视频号", "contribution": 20.1}, {"channel": "微信", "contribution": 13.2}]}, {"name": "线性归因", "channels": [{"channel": "抖音", "contribution": 41.8}, {"channel": "小红书", "contribution": 25.5}, {"channel": "视频号", "contribution": 19.3}, {"channel": "微信", "contribution": 13.4}]}, {"name": "时间衰减", "channels": [{"channel": "抖音", "contribution": 35.2}, {"channel": "小红书", "contribution": 30.1}, {"channel": "视频号", "contribution": 21.8}, {"channel": "微信", "contribution": 12.9}]}], "recommendation": "抖音渠道贡献度最高，建议在抖音渠道增加20%投放预算；小红书末次触达转化力强，适合做种草内容。"}}


@router.get("/analytics/roi")
def analytics_roi():
    return {"success": True, "data": {"total_gmv": 1286000, "total_cost": 320000, "overall_roi": 4.02, "channels": [{"channel": "抖音", "cost": 150000, "gmv": 680000, "roi": 4.53}, {"channel": "小红书", "cost": 80000, "gmv": 350000, "roi": 4.38}, {"channel": "视频号", "cost": 50000, "gmv": 180000, "roi": 3.60}, {"channel": "微信", "cost": 40000, "gmv": 76000, "roi": 1.90}], "advice": "微信渠道ROI偏低，建议优化内容策略或减少投入，将预算向抖音和小红书倾斜。"}}
