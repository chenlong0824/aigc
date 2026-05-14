import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import engine, Base, SessionLocal
from app.models.models import Media
from app.config import MEDIA_DIR

Base.metadata.create_all(bind=engine)

db = SessionLocal()

IMAGES_DIR = os.path.join(MEDIA_DIR, "images")

INITIAL_MEDIA = [
    {"name": "lishiyiji-maoling.png", "tags": "茂陵 汉武帝 陵墓 遗址 石雕 历史"},
    {"name": "lishiyiji-maoling1.png", "tags": "茂陵 汉武帝 陵墓 遗址 石雕 历史"},
    {"name": "lishiyiji-maoling2.jpg", "tags": "茂陵 汉武帝 陵墓 遗址 石雕 历史"},
    {"name": "lishiyiji-qianling.png", "tags": "乾陵 武则天 陵墓 石像生 无字碑 历史"},
    {"name": "lishiyiji-qianling1.png", "tags": "乾陵 武则天 陵墓 石像生 无字碑 历史"},
    {"name": "chengshifengmao-jiedao.jpg", "tags": "咸阳 Xianyang 城市 博物馆 街道 建筑"},
    {"name": "chengshifengmao-jiedao1.jpg", "tags": "咸阳 Xianyang 城市 博物馆 街道 建筑"},
    {"name": "chengshifengmao-jiedao2.png", "tags": "咸阳 Xianyang 城市 博物馆 街道 建筑"},
    {"name": "chengshifengmao-jiedao3.jpg", "tags": "咸阳 Xianyang 城市 博物馆 街道 建筑"},
    {"name": "jiaotongchuxing-jichang.png", "tags": "机场 airport 交通 地铁 公路 自驾"},
    {"name": "jiaotongchuxing-jichang1.png", "tags": "机场 airport 交通 地铁 公路 自驾"},
    {"name": "jiaotongchuxing-jichang2.png", "tags": "机场 airport 交通 地铁 公路 自驾"},
    {"name": "jiaotongchuxing-jichang3.png", "tags": "机场 airport 交通 地铁 公路 自驾"},
    {"name": "meishixiaochi-doufunao.png", "tags": "美食 汇通面 小吃 夜市 锅盔 豆腐脑"},
    {"name": "meishixiaochi-huitongmian.jpg", "tags": "美食 汇通面 小吃 夜市 锅盔 豆腐脑"},
    {"name": "meishixiaochi-kaorou.jpg", "tags": "美食 汇通面 小吃 夜市 锅盔 豆腐脑"},
    {"name": "meishixiaochi-shousi.jpg", "tags": "美食 汇通面 小吃 夜市 锅盔 豆腐脑"},
    {"name": "meishixiaochi-tudou.png", "tags": "美食 汇通面 小吃 夜市 锅盔 豆腐脑"},
    {"name": "wenlvhuodong-miaohui.jpg", "tags": "活动 庙会 非遗 表演 音乐喷泉 人群"},
    {"name": "wenlvhuodong-miaohui1.png", "tags": "活动 庙会 非遗 表演 音乐喷泉 人群"},
    {"name": "wenlvhuodong-miaohui2.jpg", "tags": "活动 庙会 非遗 表演 音乐喷泉 人群"},
    {"name": "wenlvhuodong-miaohui3.jpg", "tags": "活动 庙会 非遗 表演 音乐喷泉 人群"},
    {"name": "xiangcunguzhen-yuanjiacun.jpg", "tags": "袁家村 YuanJiaCun 古镇 民俗 老街 关中 美食"},
    {"name": "xiangcunguzhen-yuanjiacun1.jpg", "tags": "袁家村 YuanJiaCun 古镇 民俗 老街 关中 美食"},
    {"name": "xiangcunguzhen-yuanjiacun2.jpg", "tags": "袁家村 YuanJiaCun 古镇 民俗 老街 关中 美食"},
    {"name": "xiangcunguzhen-yuanjiacun3.jpg", "tags": "袁家村 YuanJiaCun 古镇 民俗 老街 关中 美食"},
    {"name": "xiangcunguzhen-yuanjiacun4.jpg", "tags": "袁家村 YuanJiaCun 古镇 民俗 老街 关中 美食"},
    {"name": "ziranfengguang-xianyanghu.jpg", "tags": "咸阳湖 lake 湖面 湿地 夕阳 自然 风光"},
    {"name": "ziranfengguang-xianyanghu1.jpg", "tags": "咸阳湖 lake 湖面 湿地 夕阳 自然 风光"},
    {"name": "ziranfengguang-xianyanghu2.jpg", "tags": "咸阳湖 lake 湖面 湿地 夕阳 自然 风光"},
    {"name": "ziranfengguang-xianyanghu3.jpg", "tags": "咸阳湖 lake 湖面 湿地 夕阳 自然 风光"},
    {"name": "ziranfengguang-xianyanghu4.jpg", "tags": "咸阳湖 lake 湖面 湿地 夕阳 自然 风光"},
]

count = 0
skipped = 0

for item in INITIAL_MEDIA:
    target_name = item["name"]

    existing = db.query(Media).filter(Media.name == target_name).first()
    if existing:
        skipped += 1
        continue

    found = None
    for fname in os.listdir(IMAGES_DIR):
        if fname.endswith("_" + target_name):
            found = fname
            break

    if not found:
        print(f"  [WARN] 未找到图片文件: {target_name}")
        continue

    file_path = os.path.join(IMAGES_DIR, found)
    media = Media(
        name=target_name,
        type="image",
        file_path=file_path,
        tags=item["tags"],
    )
    db.add(media)
    count += 1

db.commit()
db.close()

print(f"Media种子数据完成: 新增 {count}, 已存在跳过 {skipped}, 总计 {len(INITIAL_MEDIA)}")
