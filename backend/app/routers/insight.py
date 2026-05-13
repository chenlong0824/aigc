from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_topics as ai_generate_topics

router = APIRouter()


class AdoptTopicRequest(BaseModel):
    title: str
    reason: str
    audience: str
    publish_time: str
    score: int


@router.get("/profiles")
def get_profiles():
    return {"success": True, "data": {"overview": {"total_users": 285000, "active_users": 128000, "avg_session_duration": 186}, "user_segments": [{"name": "周边自驾家庭", "percentage": 42, "tags": ["亲子", "自然", "周末"], "avg_consumption": "200-500元", "active_time": "周五晚", "interests": ["户外活动", "亲子乐园", "特色美食"]}, {"name": "省外研学团", "percentage": 18, "tags": ["历史", "博物馆", "教育"], "avg_consumption": "500-1000元", "active_time": "工作日", "interests": ["历史文化", "博物馆", "非遗体验"]}, {"name": "年轻打卡族", "percentage": 25, "tags": ["网红", "美食", "拍照"], "avg_consumption": "100-300元", "active_time": "全时段", "interests": ["网红打卡", "美食探店", "拍照圣地"]}, {"name": "退休银发团", "percentage": 15, "tags": ["文化", "慢游", "养生"], "avg_consumption": "300-800元", "active_time": "工作日", "interests": ["文化古迹", "养生度假", "乡村休闲"]}], "source_distribution": {"陕西周边": 45, "华北": 18, "华东": 15, "华南": 10, "西南": 8, "其他": 4}, "age_distribution": {"18-25": 22, "26-35": 35, "36-50": 28, "50+": 15}}}


@router.get("/topics")
async def get_topics():
    topics = await ai_generate_topics()

    if not topics:
        topics = [{"title": "咸阳春日赏花路线", "reason": "春季赏花热点+咸阳万亩油菜花盛开", "audience": "自驾家庭、年轻情侣", "publish_time": "周五18:00", "score": 92}, {"title": "袁家村非遗美食之旅", "reason": "非遗文化热度+美食类内容高互动", "audience": "美食爱好者、打卡族", "publish_time": "周六10:00", "score": 88}, {"title": "乾陵探秘-寻找无字碑的秘密", "reason": "历史文化类长尾流量+悬疑感标题", "audience": "研学团、历史文化爱好者", "publish_time": "周三12:00", "score": 85}, {"title": "咸阳湖落日打卡攻略", "reason": "落日美景天然流量+打卡类内容易传播", "audience": "青年群体、摄影爱好者", "publish_time": "周五17:00", "score": 80}, {"title": "周末咸阳一日游路线", "reason": "周末周边游刚需+实用攻略类高收藏", "audience": "西安周边白领、家庭", "publish_time": "周四20:00", "score": 78}]

    return {"success": True, "data": topics}


@router.post("/topics/adopt")
def adopt_topic(req: AdoptTopicRequest):
    return {"success": True, "data": {"topic": req.title, "message": "选题已采纳，请前往内容工厂开始创作"}}
