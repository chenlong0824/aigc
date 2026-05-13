from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import uuid
import asyncio
import os
import shutil
import platform
from app.services.llm_service import generate_script
from app.services.tts_service import generate_tts
from app.database import get_db, get_db_session
from app.models.models import Template, Task, Media
from app.config import FFMPEG_PATH, VIDEO_OUTPUT_DIR, MEDIA_DIR

router = APIRouter()


def _get_chinese_font_path():
    """跨平台获取中文字体路径"""
    system = platform.system()
    if system == "Windows":
        candidates = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


class ScriptRequest(BaseModel):
    """生成文案请求模型"""
    topic: str
    style: Optional[str] = "探店"


class ComposeRequest(BaseModel):
    """视频合成请求模型"""
    topic: str
    template_id: int
    style: Optional[str] = "探店"


class DigitalHumanRequest(BaseModel):
    """数智人生成请求模型"""
    avatar_id: str
    script: str


@router.post("/generate-script")
async def create_script(req: ScriptRequest):
    """
    生成短视频分镜文案
    
    Args:
        req: 包含主题和风格的请求
        
    Returns:
        生成的脚本数据
    """
    script = await generate_script(req.topic, req.style)
    return {"success": True, "data": script}


@router.get("/templates")
def list_templates():
    """获取视频模板列表"""
    db = next(get_db())
    try:
        templates = db.query(Template).all()
        return {"success": True, "data": [{"id": t.id, "name": t.name, "style": t.style, "config": t.config} for t in templates]}
    finally:
        db.close()


@router.get("/media")
def list_media(type: Optional[str] = None, tag: Optional[str] = None):
    """
    获取媒体素材列表
    
    Args:
        type: 素材类型（image/video）
        tag: 标签筛选
        
    Returns:
        素材列表
    """
    db = next(get_db())
    try:
        query = db.query(Media)
        if type:
            query = query.filter(Media.type == type)
        if tag:
            query = query.filter(Media.tags.contains(tag))
        media_list = query.all()
        return {"success": True, "data": [{"id": m.id, "name": m.name, "type": m.type, "file_path": m.file_path, "tags": m.tags, "duration": m.duration} for m in media_list]}
    finally:
        db.close()


@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    tags: str = Form(""),
    name: str = Form(""),
):
    """
    上传媒体素材
    
    Args:
        file: 上传的文件
        tags: 素材标签
        name: 素材名称
        
    Returns:
        上传成功后的素材信息
    """
    # 根据文件扩展名判断素材类型
    ext = os.path.splitext(file.filename or "unknown.jpg")[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        media_type = "image"
        save_dir = os.path.join(MEDIA_DIR, "images")
    elif ext in (".mp4", ".mov", ".avi", ".webm"):
        media_type = "video"
        save_dir = os.path.join(MEDIA_DIR, "videos")
    else:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    # 创建保存目录并保存文件
    os.makedirs(save_dir, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    save_path = os.path.join(save_dir, safe_name)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    display_name = name or file.filename or safe_name

    # 保存素材信息到数据库
    with get_db_session() as db:
        media = Media(name=display_name, type=media_type, file_path=save_path, tags=tags)
        db.add(media)
        db.commit()
        db.refresh(media)

        return {"success": True, "data": {"id": media.id, "name": media.name, "type": media.type, "file_path": media.file_path, "tags": media.tags}}


@router.delete("/media/{media_id}")
def delete_media(media_id: int):
    """
    删除媒体素材
    
    Args:
        media_id: 素材ID
    """
    with get_db_session() as db:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="素材不存在")
        # 删除文件
        if os.path.exists(media.file_path):
            os.remove(media.file_path)
        # 删除数据库记录
        db.delete(media)
        db.commit()
        return {"success": True, "message": "删除成功"}


class MediaUpdateRequest(BaseModel):
    """更新素材请求模型"""
    tags: Optional[str] = None
    name: Optional[str] = None


@router.put("/media/{media_id}")
def update_media_tags(media_id: int, req: MediaUpdateRequest):
    """
    更新媒体素材信息
    
    Args:
        media_id: 素材ID
        req: 更新信息
        
    Returns:
        更新后的素材信息
    """
    with get_db_session() as db:
        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="素材不存在")
        if req.tags:
            media.tags = req.tags
        if req.name:
            media.name = req.name
        db.commit()
        return {"success": True, "data": {"id": media.id, "name": media.name, "tags": media.tags}}


def _extract_chinese_keywords(text: str):
    """
    从中文文本中提取关键词用于模糊匹配
    
    Args:
        text: 输入文本
        
    Returns:
        提取的关键词列表
    """
    clean = ""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff' or ch == ' ':
            clean += ch
        elif ch.isalpha():
            clean += ' ' + ch + ' '
    kws = set()
    parts = clean.split()
    for p in parts:
        p = p.strip()
        p_lower = p.lower()
        kws.add(p_lower)
        for i in range(len(p) - 1):
            bigram = p[i:i+2]
            if len(bigram) >= 2:
                kws.add(bigram.lower())
    return list(kws)


def match_media_for_scene(db_session, subtitle: str, description: str, used_ids: list, media_type: str = "image", limit: int = 2):
    """
    为分镜匹配相关素材
    
    Args:
        db_session: 数据库会话
        subtitle: 分镜字幕
        description: 分镜描述
        used_ids: 已使用的素材ID列表
        media_type: 素材类型
        limit: 最多返回数量
        
    Returns:
        匹配的素材列表（按匹配度排序）
    """
    # 从字幕和描述中提取关键词
    keywords = _extract_chinese_keywords(subtitle)
    keywords += _extract_chinese_keywords(description)

    # 获取所有同类型素材
    all_media = db_session.query(Media).filter(Media.type == media_type).all()

    # 计算匹配分数
    scored = []
    for m in all_media:
        if m.id in used_ids:
            continue
        score = 0
        tag_str = (m.tags or "") + " " + (m.name or "")
        tag_lower = tag_str.lower()
        for kw in keywords:
            if kw in tag_lower:
                score += 1
        if score > 0:
            scored.append((score, m))

    # 按分数降序排序
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:max(limit, 1)]]


@router.post("/compose-video")
async def compose_video(req: ComposeRequest):
    """
    合成短视频
    
    Args:
        req: 合成请求
        
    Returns:
        合成任务信息
    """
    db = next(get_db())

    import json
    # 生成脚本
    script = await generate_script(req.topic, req.style)

    # 创建任务记录
    task = Task(
        type="one_click",
        title=req.topic,
        input_data=f'{{"topic": "{req.topic}", "style": "{req.style}", "template_id": {req.template_id}}}',
        status="processing"
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        import subprocess
        import os
        ffmpeg_exe = FFMPEG_PATH
        # 检查FFmpeg是否安装
        if not os.path.exists(ffmpeg_exe):
            task.status = "failed"
            task.output_data = '{"message": "FFmpeg未安装，视频合成失败", "mock": true}'
            task.output_path = ""
            db.commit()
            return {"success": False, "message": "FFmpeg未安装，无法合成视频"}
        output_filename = f"video_{task.id}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(VIDEO_OUTPUT_DIR, output_filename)

        scenes = script.get("scenes", [])
        font_path = _get_chinese_font_path()
        if font_path:
            fontfile_ff = font_path.replace("\\", "/")
        else:
            fontfile_ff = None
        colors = ["#0f3460", "#16213e", "#1a1a2e", "#533483", "#e94560"]

        scene_files = []
        tts_lines = []
        used_media = []

        # 打乱素材顺序，避免重复
        import random
        all_db_images = db.query(Media).filter(Media.type == "image").all()
        random.shuffle(all_db_images)

        # 逐个处理每个分镜
        for i, scene in enumerate(scenes):
            duration = max(float(scene.get("duration", 3)), 2)
            subtitle = scene.get("subtitle", f"Scene {i+1}")
            description = scene.get("description", "")

            scene_file = os.path.join(VIDEO_OUTPUT_DIR, f"_s_{task.id}_{i}.mp4")
            scene_files.append(scene_file)
            tts_lines.append(subtitle)

            # 为当前分镜匹配素材
            matched_images = match_media_for_scene(db, subtitle, description, used_media, "image", limit=2)

            # 转义字幕中的特殊字符
            sf = subtitle.replace("'", "").replace("\\", "").replace(":", " ").replace("%", " ")

            # 构建FFmpeg的文字叠加滤镜
            if fontfile_ff:
                font_part = f"fontfile='{fontfile_ff}':"
            else:
                font_part = ""
            drawtext = (
                f"drawtext={font_part}"
                f"text={sf}"
                ":fontsize=38:fontcolor=white"
                ":x=(w-text_w)/2:y=(h-text_h)/2-80"
                ":box=1:boxcolor=black@0.35:boxborderw=16"
                f",drawtext={font_part}"
                f"text=分镜 {i+1}/{len(scenes)}"
                ":fontsize=18:fontcolor=#aaaaaa"
                ":x=(w-text_w)/2:y=(h-text_h)/2+30"
            )

            # 检查匹配到的素材文件是否存在
            if matched_images:
                img_path = matched_images[0].file_path
                if not os.path.exists(img_path):
                    matched_images = []

            # 如果没有匹配到，从未使用的素材中选择
            if not matched_images:
                for mi in all_db_images:
                    if mi.id not in used_media and os.path.exists(mi.file_path):
                        matched_images = [mi]
                        break

            if matched_images:
                img_path = matched_images[0].file_path
                if not os.path.exists(img_path):
                    img_path = None

            # 使用匹配到的图片或纯色背景生成分镜视频
            if img_path:
                used_media.append(matched_images[0].id)
                cmd = [
                    ffmpeg_exe, "-y",
                    "-loop", "1", "-i", img_path,
                    "-t", str(duration),
                    "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*25)}:s=1080x1920:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',fps=25,{drawtext}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "ultrafast",
                    scene_file
                ]
            else:
                color = colors[i % len(colors)]
                cmd = [
                    ffmpeg_exe, "-y",
                    "-f", "lavfi", "-i", f"color=c={color}:s=1080x1920:d={duration}:r=25",
                    "-vf", drawtext,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "ultrafast",
                    scene_file
                ]

            # 执行FFmpeg命令生成分镜
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                task.status = "failed"
                task.output_data = json.dumps({"error": f"Scene {i} failed", "stderr": result.stderr[:400]}, ensure_ascii=False)
                db.commit()
                # 清理已生成的分镜文件
                for f in scene_files:
                    if os.path.exists(f):
                        os.remove(f)
                return {"success": False, "message": f"分镜{i+1}失败: {result.stderr[:150]}"}

        # 创建拼接文件列表
        concat_list = os.path.join(VIDEO_OUTPUT_DIR, f"_cl_{task.id}.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for sf in scene_files:
                f.write(f"file '{sf}'\n")

        # 拼接所有分镜
        concat_result = subprocess.run(
            [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
             "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path],
            capture_output=True, text=True, timeout=60
        )

        if concat_result.returncode != 0 or not os.path.exists(output_path):
            task.status = "failed"
            task.output_data = json.dumps({"error": "Concat failed", "stderr": concat_result.stderr[:500]}, ensure_ascii=False)
            db.commit()
            return {"success": False, "message": f"拼接失败: {concat_result.stderr[:200]}"}

        # 生成并合成音频
        try:
            tts_text = "  ".join(tts_lines)
            audio_path = await generate_tts(tts_text, f"va_{task.id}")
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
                temp_video = output_path + ".tmp.mp4"
                os.rename(output_path, temp_video)
                merge_result = subprocess.run(
                    [ffmpeg_exe, "-y", "-i", temp_video, "-i", audio_path,
                     "-c:v", "copy", "-c:a", "aac", "-shortest", output_path],
                    capture_output=True, text=True, timeout=30
                )
                if merge_result.returncode != 0 or not os.path.exists(output_path):
                    os.rename(temp_video, output_path)
                elif os.path.exists(temp_video):
                    os.remove(temp_video)
        except Exception:
            pass

        # 清理临时文件
        for sf in scene_files:
            if os.path.exists(sf):
                os.remove(sf)
        if os.path.exists(concat_list):
            os.remove(concat_list)

        # 更新任务状态
        task.status = "completed"
        task.output_path = output_path
        has_real_media = len(used_media) > 0
        task.output_data = json.dumps(
            {"message": "视频合成成功", "script": script, "scenes_count": len(scenes),
             "used_real_images": has_real_media, "matched_count": len(used_media)},
            ensure_ascii=False
        )
        db.commit()
        return {"success": True, "data": {"task_id": task.id, "status": "completed", "output_path": output_path, "script": script, "used_real_images": has_real_media, "matched_count": len(used_media)}}
    except Exception as e:
        task.status = "failed"
        task.output_data = str(e)
        db.commit()
        return {"success": False, "message": str(e)}
    finally:
        db.close()


@router.get("/tasks")
def list_tasks(type: Optional[str] = None, status: Optional[str] = None):
    """
    获取任务列表
    
    Args:
        type: 任务类型
        status: 任务状态
        
    Returns:
        任务列表
    """
    with get_db_session() as db:
        query = db.query(Task)
        if type:
            query = query.filter(Task.type == type)
        if status:
            query = query.filter(Task.status == status)
        tasks = query.order_by(Task.created_at.desc()).all()
        return {"success": True, "data": [{"id": t.id, "type": t.type, "title": t.title, "status": t.status, "input_data": t.input_data, "output_data": t.output_data, "created_at": str(t.created_at)} for t in tasks]}


@router.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    获取单个任务详情
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务详情
    """
    with get_db_session() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {"success": True, "data": {"id": task.id, "type": task.type, "title": task.title, "status": task.status, "input_data": task.input_data, "output_data": task.output_data, "output_path": task.output_path, "created_at": str(task.created_at)}}


@router.get("/tasks/{task_id}/download")
def download_task(task_id: int):
    """
    下载任务生成的视频
    
    Args:
        task_id: 任务ID
        
    Returns:
        视频文件
    """
    from fastapi.responses import FileResponse
    with get_db_session() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task or not task.output_path:
            raise HTTPException(status_code=404, detail="文件不存在")
        return FileResponse(task.output_path, media_type="video/mp4", filename=f"video_{task_id}.mp4")


@router.post("/digital-human/generate")
async def generate_digital_human(req: DigitalHumanRequest):
    """
    生成数智人视频
    
    Args:
        req: 生成请求
        
    Returns:
        任务信息
    """
    db = next(get_db())
    # 创建任务记录
    task = Task(type="digital_human", title=f"数智人播报-{req.script[:20]}", input_data=f'{{"avatar_id": "{req.avatar_id}", "script": "{req.script}"}}', status="processing")
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        import subprocess
        import os
        ffmpeg_exe = FFMPEG_PATH
        # 检查FFmpeg是否安装
        if not os.path.exists(ffmpeg_exe):
            task.status = "failed"
            task.output_data = '{"message": "FFmpeg未安装，数智人视频合成失败", "mock": true}'
            db.commit()
            return {"success": False, "data": {"task_id": task.id, "status": "failed", "message": "FFmpeg未安装，无法合成数智人视频"}}

        # 生成TTS音频
        audio_path = await generate_tts(req.script, f"digital_{task.id}")

        # 设置输出文件
        output_filename = f"digital_{task.id}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(VIDEO_OUTPUT_DIR, output_filename)

        # 使用FFmpeg生成演示视频
        font_path = _get_chinese_font_path()
        if font_path:
            font_part = f"fontfile='{font_path.replace(chr(92), '/')}':"
        else:
            font_part = ""
        script_preview = req.script[:40] + ("..." if len(req.script) > 40 else "")
        safe_preview = script_preview.replace("'", "").replace('"', "")
        cmd = [
            ffmpeg_exe, "-y",
            "-f", "lavfi", "-i", "color=c=#1a1a2e:s=1920x1080:d=8",
            "-vf", f"drawtext=text='XianYang Digital Human':{font_part}fontsize=36:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-60,drawtext=text='Demo Broadcast':{font_part}fontsize=28:fontcolor=#e94560:x=(w-text_w)/2:y=(h-text_h)/2+10",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(output_path):
            task.status = "failed"
            task.output_data = json.dumps({"error": "FFmpeg 执行失败", "stderr": result.stderr[:500] if result.stderr else ""}, ensure_ascii=False)
            db.commit()
            return {"success": False, "message": f"视频合成失败: {result.stderr[:200]}"}

        # 更新任务状态
        task.status = "completed"
        task.output_path = output_path
        task.output_data = '{"message": "数智人视频生成成功"}'
        db.commit()
        return {"success": True, "data": {"task_id": task.id, "status": "completed", "output_path": output_path}}
    except Exception as e:
        task.status = "failed"
        task.output_data = str(e)
        db.commit()
        return {"success": False, "message": str(e)}
    finally:
        db.close()


@router.get("/digital-human/avatars")
def list_avatars():
    """获取可用的数智人形象列表"""
    return {"success": True, "data": [{"id": "avatar_1", "name": "端庄新闻型", "scene": "天气预警"}, {"id": "avatar_2", "name": "亲和导游型", "scene": "客流提醒"}, {"id": "avatar_3", "name": "活泼主持型", "scene": "活动预告"}]}
