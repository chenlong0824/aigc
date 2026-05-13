import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import engine, Base, SessionLocal
from app.models.models import Template, Account, CreatorRanking

Base.metadata.create_all(bind=engine)

db = SessionLocal()

templates_data = [
    {"name": "快节奏探店", "style": "探店", "config": '{"duration_range":[15,30],"bgm_style":"fast","transitions":"quick","subtitle_style":"large"}'},
    {"name": "唯美航拍", "style": "航拍", "config": '{"duration_range":[20,40],"bgm_style":"slow","transitions":"fade","subtitle_style":"poem"}'},
    {"name": "故事讲述", "style": "故事", "config": '{"duration_range":[30,60],"bgm_style":"narrative","transitions":"soft","subtitle_style":"emotional"}'},
]

for t in templates_data:
    existing = db.query(Template).filter(Template.name == t["name"]).first()
    if not existing:
        db.add(Template(**t))

accounts_data = [
    {"name": "咸阳文旅-欧美号", "platform": "抖音", "group_name": "客源地", "followers": 23000},
    {"name": "咸阳味道", "platform": "小红书", "group_name": "美食", "followers": 18000},
    {"name": "咸阳研学游", "platform": "视频号", "group_name": "研学", "followers": 6000},
    {"name": "西安周边游攻略", "platform": "抖音", "group_name": "周边", "followers": 52000},
    {"name": "咸阳文旅-日韩号", "platform": "抖音", "group_name": "客源地", "followers": 15000},
    {"name": "咸阳非遗传承", "platform": "视频号", "group_name": "文化", "followers": 8500},
    {"name": "咸阳周末去哪", "platform": "小红书", "group_name": "周边", "followers": 32000},
    {"name": "咸阳四季美景", "platform": "抖音", "group_name": "风光", "followers": 48000},
]

for a in accounts_data:
    existing = db.query(Account).filter(Account.name == a["name"]).first()
    if not existing:
        db.add(Account(**a))

rankings_data = [
    {"user_name": "旅行达人小王", "works_count": 12, "total_likes": 3600, "points": 1280},
    {"user_name": "咸阳本地通", "works_count": 8, "total_likes": 2800, "points": 960},
    {"user_name": "摄影爱好者", "works_count": 15, "total_likes": 2100, "points": 850},
    {"user_name": "美食探店家", "works_count": 10, "total_likes": 1800, "points": 720},
    {"user_name": "文旅创客小明", "works_count": 6, "total_likes": 1500, "points": 560},
]

for r in rankings_data:
    existing = db.query(CreatorRanking).filter(CreatorRanking.user_name == r["user_name"]).first()
    if not existing:
        db.add(CreatorRanking(**r))

db.commit()
db.close()

print("种子数据初始化完成！")
