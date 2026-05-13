from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db, get_db_session
from app.models.models import Account, PublishLog, Task, CreatorRanking

router = APIRouter()


class AccountCreate(BaseModel):
    name: str
    platform: str
    group_name: Optional[str] = ""
    followers: Optional[int] = 0


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    group_name: Optional[str] = None
    followers: Optional[int] = None
    status: Optional[str] = None


class SchedulePublish(BaseModel):
    account_id: int
    content_id: Optional[int] = None
    content_title: Optional[str] = ""
    scheduled_at: str


@router.get("/accounts")
def list_accounts():
    with get_db_session() as db:
        accounts = db.query(Account).all()
        return {"success": True, "data": [{"id": a.id, "name": a.name, "platform": a.platform, "group_name": a.group_name, "followers": a.followers, "status": a.status, "created_at": str(a.created_at)} for a in accounts]}


@router.post("/accounts")
def create_account(req: AccountCreate):
    with get_db_session() as db:
        account = Account(name=req.name, platform=req.platform, group_name=req.group_name, followers=req.followers)
        db.add(account)
        db.commit()
        db.refresh(account)
        return {"success": True, "data": {"id": account.id, "name": account.name}}


@router.put("/accounts/{account_id}")
def update_account(account_id: int, req: AccountUpdate):
    with get_db_session() as db:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        if req.name is not None:
            account.name = req.name
        if req.platform is not None:
            account.platform = req.platform
        if req.group_name is not None:
            account.group_name = req.group_name
        if req.followers is not None:
            account.followers = req.followers
        if req.status is not None:
            account.status = req.status
        db.commit()
        return {"success": True, "message": "更新成功"}


@router.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    with get_db_session() as db:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        db.delete(account)
        db.commit()
        return {"success": True, "message": "删除成功"}


@router.post("/accounts/schedule-publish")
def schedule_publish(req: SchedulePublish):
    with get_db_session() as db:
        try:
            scheduled_dt = datetime.fromisoformat(req.scheduled_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="发布时间格式错误，请使用 ISO 格式")

        log = PublishLog(
            account_id=req.account_id,
            content_id=req.content_id,
            content_title=req.content_title,
            status="pending",
            scheduled_at=scheduled_dt,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        import asyncio

        async def simulate_publish(log_id: int):
            await asyncio.sleep(2)
            with get_db_session() as db2:
                try:
                    log2 = db2.query(PublishLog).filter(PublishLog.id == log_id).first()
                    if log2:
                        log2.status = "success"
                        log2.published_at = datetime.now()
                        db2.commit()
                finally:
                    pass

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(simulate_publish(log.id))
        except RuntimeError:
            pass

        return {"success": True, "data": {"id": log.id, "status": "pending", "message": "已加入发布队列"}}


@router.get("/accounts/publish-logs")
def list_publish_logs(account_id: Optional[int] = None):
    with get_db_session() as db:
        query = db.query(PublishLog)
        if account_id:
            query = query.filter(PublishLog.account_id == account_id)
        logs = query.order_by(PublishLog.created_at.desc()).all()
        return {"success": True, "data": [{"id": l.id, "account_id": l.account_id, "content_title": l.content_title, "status": l.status, "scheduled_at": str(l.scheduled_at) if l.scheduled_at else None, "published_at": str(l.published_at) if l.published_at else None, "created_at": str(l.created_at)} for l in logs]}


@router.get("/reports/overview")
def reports_overview():
    return {"success": True, "data": {"total_views": 1285600, "total_likes": 89600, "total_comments": 12300, "total_shares": 34500, "new_followers": 5600, "period_growth": 12.5, "accounts_active": 8, "content_published": 126}}


@router.get("/reports/anomalies")
def reports_anomalies():
    return {"success": True, "data": [{"account_name": "咸阳美食号", "platform": "抖音", "metric": "点赞数", "value": 23000, "expected": 3000, "reason": "点赞量异常暴增，疑似刷量"}, {"account_name": "咸阳研学游", "platform": "视频号", "metric": "评论数", "value": 0, "expected": 50, "reason": "播放5000但评论为0，数据异常"}]}


@router.get("/reports/rankings")
def creator_rankings():
    with get_db_session() as db:
        rankings = db.query(CreatorRanking).order_by(CreatorRanking.points.desc()).all()
        if not rankings:
            return {"success": True, "data": [{"user_name": "旅行达人小王", "works_count": 12, "total_likes": 3600, "points": 1280}, {"user_name": "咸阳本地通", "works_count": 8, "total_likes": 2800, "points": 960}, {"user_name": "摄影爱好者", "works_count": 15, "total_likes": 2100, "points": 850}]}
        return {"success": True, "data": [{"id": r.id, "user_name": r.user_name, "works_count": r.works_count, "total_likes": r.total_likes, "points": r.points} for r in rankings]}
