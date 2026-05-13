import os
from pathlib import Path

# 加载 .env 文件
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# 基础目录配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MEDIA_DIR = os.path.join(DATA_DIR, "media")
DB_DIR = os.path.join(DATA_DIR, "db")

# 数据库配置
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'aigc.db')}"

# Ollama配置（本地模型）
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:2b")

# AI模型提供商配置
# 可选值: "ollama" (本地) 或 "qwen" (云端千问)
AI_MODEL_PROVIDER = os.getenv("AI_MODEL_PROVIDER", "ollama")

# 千问云端配置（阿里云 DashScope）
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# ChromaDB向量数据库配置
CHROMA_PERSIST_DIR = os.path.join(DB_DIR, "chroma")

# FFmpeg路径配置
FFMPEG_PATH = os.getenv("FFMPEG_PATH", r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe")

# 输出目录配置
TTS_OUTPUT_DIR = os.path.join(MEDIA_DIR, "audio")
VIDEO_OUTPUT_DIR = os.path.join(MEDIA_DIR, "videos")

# 确保输出目录存在
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)
