from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class Media(Base):
    """媒体素材模型"""
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # 素材名称
    type = Column(String(20), nullable=False)  # 素材类型（image/video）
    file_path = Column(String(500), nullable=False)  # 文件路径
    tags = Column(Text)  # 标签，逗号分隔
    duration = Column(Float)  # 时长（视频）
    created_at = Column(DateTime, server_default=func.now())  # 创建时间


class Template(Base):
    """视频模板模型"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # 模板名称
    style = Column(String(50), nullable=False)  # 风格
    config = Column(Text, nullable=False)  # 配置（JSON）
    created_at = Column(DateTime, server_default=func.now())  # 创建时间


class Task(Base):
    """任务模型（视频合成/数智人）"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)  # 任务类型（one_click/digital_human）
    title = Column(String(500))  # 标题
    input_data = Column(Text)  # 输入数据（JSON）
    output_data = Column(Text)  # 输出数据（JSON）
    output_path = Column(String(500))  # 输出文件路径
    status = Column(String(20), default="pending")  # 状态（pending/processing/completed/failed）
    created_at = Column(DateTime, server_default=func.now())  # 创建时间
    finished_at = Column(DateTime)  # 完成时间


class Account(Base):
    """社交账号模型"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # 账号名称
    platform = Column(String(50), nullable=False)  # 平台（抖音/快手/视频号等）
    group_name = Column(String(100))  # 分组名称
    avatar = Column(String(500))  # 头像路径
    followers = Column(Integer, default=0)  # 粉丝数
    status = Column(String(20), default="active")  # 状态
    created_at = Column(DateTime, server_default=func.now())  # 创建时间


class PublishLog(Base):
    """发布日志模型"""
    __tablename__ = "publish_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)  # 账号ID
    content_id = Column(Integer, ForeignKey("tasks.id"))  # 内容ID
    content_title = Column(String(500))  # 内容标题
    status = Column(String(20), default="pending")  # 状态
    scheduled_at = Column(DateTime)  # 计划发布时间
    published_at = Column(DateTime)  # 实际发布时间
    created_at = Column(DateTime, server_default=func.now())  # 创建时间


class ChatSession(Base):
    """客服会话模型"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False)  # 会话ID
    user_name = Column(String(100))  # 用户名称
    messages = Column(Text)  # 消息记录（JSON）
    created_at = Column(DateTime, server_default=func.now())  # 创建时间


class CreatorRanking(Base):
    """创作者排行榜模型"""
    __tablename__ = "creator_rankings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(100), nullable=False)  # 用户名称
    works_count = Column(Integer, default=0)  # 作品数
    total_likes = Column(Integer, default=0)  # 总点赞数
    points = Column(Integer, default=0)  # 积分
    created_at = Column(DateTime, server_default=func.now())  # 创建时间
