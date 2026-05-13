from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
def dashboard_summary():
    return {"success": True, "data": {"content_factory": {"videos_generated": 48, "digital_human_videos": 12, "active_templates": 3, "pending_tasks": 2}, "distribution": {"accounts_count": 8, "today_published": 12, "total_published": 126, "avg_engagement_rate": "4.8%"}, "conversion": {"total_gmv": 1286000, "booking_count": 4100, "consultations": 25600, "conversion_rate": "0.32%"}, "insight": {"user_segments": 4, "hot_topics": 12, "avg_crowd_score": 85}}}


@router.get("/trends")
def dashboard_trends():
    return {"success": True, "data": {"views_trend": [{"date": "05-05", "views": 182000}, {"date": "05-06", "views": 195000}, {"date": "05-07", "views": 210000}, {"date": "05-08", "views": 198000}, {"date": "05-09", "views": 225000}, {"date": "05-10", "views": 240000}, {"date": "05-11", "views": 265000}], "gmv_trend": [{"date": "05-05", "gmv": 168000}, {"date": "05-06", "gmv": 175000}, {"date": "05-07", "gmv": 182000}, {"date": "05-08", "gmv": 178000}, {"date": "05-09", "gmv": 195000}, {"date": "05-10", "gmv": 210000}, {"date": "05-11", "gmv": 198000}], "follower_trend": [{"date": "05-05", "followers": 102000}, {"date": "05-06", "followers": 105000}, {"date": "05-07", "followers": 109000}, {"date": "05-08", "followers": 112000}, {"date": "05-09", "followers": 116000}, {"date": "05-10", "followers": 120000}, {"date": "05-11", "followers": 126000}]}}
