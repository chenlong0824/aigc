import json
import httpx
from app.config import (
    OLLAMA_HOST, OLLAMA_MODEL,
    AI_MODEL_PROVIDER,
    QWEN_API_KEY, QWEN_MODEL, QWEN_API_BASE
)

# 脚本生成的系统提示词
SYSTEM_PROMPT = """你是咸阳文旅宣传片的专业编剧。根据用户输入的主题，生成一段短视频分镜脚本。

必须遵守：
1. 必须生成4个分镜，每个分镜用不同的画面角度和侧重点
2. subtitle用中文写出该分镜的字幕文案
3. description用中文写出该分镜的画面描述
4. duration为整数秒，建议3-6秒
5. 文案要朗朗上口，有传播力
6. 输出严格JSON格式：{"title":"标题","scenes":[{"description":"画面描述","subtitle":"字幕","duration":时长秒数}]}"""


# ==================== 统一的 AI 服务接口 ====================

async def generate_script(topic: str, style: str = "探店") -> dict:
    """
    生成短视频脚本 - 根据配置自动选择模型

    Args:
        topic: 主题
        style: 风格

    Returns:
        生成的脚本
    """
    if AI_MODEL_PROVIDER == "ollama":
        return await _generate_script_ollama(topic, style)
    else:
        return await _generate_script_qwen(topic, style)


async def chat(session_id: str, user_message: str, context: list = None) -> str:
    """
    对话功能 - 根据配置自动选择模型

    Args:
        session_id: 会话ID
        user_message: 用户消息
        context: 上下文消息

    Returns:
        回复消息
    """
    if AI_MODEL_PROVIDER == "ollama":
        return await _chat_ollama(session_id, user_message, context)
    else:
        return await _chat_qwen(session_id, user_message, context)


async def generate_topics() -> list:
    """
    生成短视频爆款选题 - 根据配置自动选择模型

    Returns:
        选题列表
    """
    if AI_MODEL_PROVIDER == "ollama":
        return await _generate_topics_ollama()
    else:
        return await _generate_topics_qwen()


def get_model_provider() -> str:
    """
    获取当前使用的模型提供商

    Returns:
        模型提供商名称： "ollama" 或 "qwen"
    """
    return AI_MODEL_PROVIDER


def set_model_provider(provider: str) -> bool:
    """
    设置模型提供商

    Args:
        provider: "ollama" 或 "qwen"

    Returns:
        是否设置成功
    """
    global AI_MODEL_PROVIDER
    if provider in ["ollama", "qwen"]:
        AI_MODEL_PROVIDER = provider
        return True
    return False


# ==================== Ollama 本地模型实现 ====================

async def _generate_script_ollama(topic: str, style: str = "探店") -> dict:
    """
    使用Ollama生成短视频分镜脚本

    Args:
        topic: 主题
        style: 风格

    Returns:
        生成的脚本
    """
    user_prompt = f"主题：{topic}\n风格：{style}\n请根据以上主题和风格生成短视频脚本。"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                    "stream": False
                }
            )
            result = response.json()
            raw_text = result.get("response", "")

            try:
                json_start = raw_text.find("{")
                json_end = raw_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    script = json.loads(raw_text[json_start:json_end])
                else:
                    script = _get_fallback_script(topic)
            except json.JSONDecodeError:
                script = _get_fallback_script(topic)

            return script
    except Exception as e:
        return _get_fallback_script(topic)


async def _chat_ollama(session_id: str, user_message: str, context: list = None) -> str:
    """
    使用Ollama进行多轮对话

    Args:
        session_id: 会话ID
        user_message: 用户消息
        context: 上下文消息

    Returns:
        回复消息
    """
    messages = context or []
    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            )
            result = response.json()
            return result.get("message", {}).get("content", "抱歉，我暂时无法回答这个问题。")
    except Exception as e:
        return "抱歉，AI服务暂时不可用，请稍后再试。"


async def _generate_topics_ollama() -> list:
    """
    使用Ollama生成短视频爆款选题

    Returns:
        选题列表
    """
    prompt = """你是咸阳文旅营销专家。请基于当前季节和热点，推荐5个短视频爆款选题。
每个选题包含：标题、推荐理由、目标人群、建议发布时间、热度评分(1-100)。
请以JSON数组格式输出：[{"title":"","reason":"","audience":"","publish_time":"","score":0}]"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            result = response.json()
            raw_text = result.get("response", "")

            try:
                json_start = raw_text.find("[")
                json_end = raw_text.rfind("]") + 1
                if json_start >= 0 and json_end > json_start:
                    topics = json.loads(raw_text[json_start:json_end])
                else:
                    topics = []
            except json.JSONDecodeError:
                topics = []

            return topics
    except Exception as e:
        return []


# ==================== 千问云端模型实现 ====================

async def _generate_script_qwen(topic: str, style: str = "探店") -> dict:
    """
    使用千问云端模型生成短视频分镜脚本

    Args:
        topic: 主题
        style: 风格

    Returns:
        生成的脚本
    """
    if not QWEN_API_KEY:
        return _get_fallback_script(topic)

    user_prompt = f"主题：{topic}\n风格：{style}\n请根据以上主题和风格生成短视频脚本。"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                QWEN_API_BASE,
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": QWEN_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            result = response.json()

            if result.get("choices") and len(result["choices"]) > 0:
                raw_text = result["choices"][0]["message"]["content"]
                try:
                    json_start = raw_text.find("{")
                    json_end = raw_text.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        script = json.loads(raw_text[json_start:json_end])
                    else:
                        script = _get_fallback_script(topic)
                except json.JSONDecodeError:
                    script = _get_fallback_script(topic)
                return script
            else:
                return _get_fallback_script(topic)

    except Exception as e:
        return _get_fallback_script(topic)


async def _chat_qwen(session_id: str, user_message: str, context: list = None) -> str:
    """
    使用千问云端模型进行对话

    Args:
        session_id: 会话ID
        user_message: 用户消息
        context: 上下文消息

    Returns:
        回复消息
    """
    if not QWEN_API_KEY:
        return "抱歉，云端模型服务未配置API Key，请联系管理员。"

    try:
        messages = context or []
        messages.append({"role": "user", "content": user_message})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                QWEN_API_BASE,
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": QWEN_MODEL,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            result = response.json()

            if result.get("choices") and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "抱歉，我暂时无法回答这个问题。"

    except Exception as e:
        return "抱歉，AI服务暂时不可用，请稍后再试。"


async def _generate_topics_qwen() -> list:
    """
    使用千问云端模型生成短视频爆款选题

    Returns:
        选题列表
    """
    if not QWEN_API_KEY:
        return []

    prompt = """你是咸阳文旅营销专家。请基于当前季节和热点，推荐5个短视频爆款选题。
每个选题包含：标题、推荐理由、目标人群、建议发布时间、热度评分(1-100)。
请以JSON数组格式输出：[{"title":"","reason":"","audience":"","publish_time":"","score":0}]"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                QWEN_API_BASE,
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": QWEN_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            result = response.json()

            if result.get("choices") and len(result["choices"]) > 0:
                raw_text = result["choices"][0]["message"]["content"]
                try:
                    json_start = raw_text.find("[")
                    json_end = raw_text.rfind("]") + 1
                    if json_start >= 0 and json_end > json_start:
                        topics = json.loads(raw_text[json_start:json_end])
                    else:
                        topics = []
                except json.JSONDecodeError:
                    topics = []
                return topics
            else:
                return []

    except Exception as e:
        return []


# ==================== 辅助函数 ====================

def _build_chat_prompt(messages: list) -> str:
    """
    构建聊天提示词

    Args:
        messages: 消息列表

    Returns:
        格式化的提示词
    """
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"系统：{content}")
        elif role == "user":
            prompt_parts.append(f"用户：{content}")
        elif role == "assistant":
            prompt_parts.append(f"助手：{content}")

    return "\n\n".join(prompt_parts)


def _get_fallback_script(topic: str) -> dict:
    """
    获取默认脚本

    Args:
        topic: 主题

    Returns:
        默认脚本
    """
    fallback_scenes = [
        {"description": f"{topic}全景展示", "subtitle": f"欢迎来到{topic}", "duration": 4},
        {"description": f"{topic}特色亮点", "subtitle": f"探索{topic}的独特魅力", "duration": 5},
        {"description": f"{topic}细节之美", "subtitle": f"每一帧都是风景", "duration": 4},
        {"description": f"{topic}精彩回顾", "subtitle": f"{topic}，等你来发现", "duration": 3},
    ]
    return {"title": topic, "scenes": fallback_scenes}
