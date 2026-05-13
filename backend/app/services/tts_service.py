import edge_tts
import os
from app.config import TTS_OUTPUT_DIR


async def generate_tts(text: str, prefix: str = "audio") -> str:
    """
    使用Edge TTS生成语音
    
    Args:
        text: 要转换的文本
        prefix: 文件名前缀
        
    Returns:
        生成的音频文件路径
    """
    # 使用中国女声
    voice = "zh-CN-XiaoxiaoNeural"
    output_file = os.path.join(TTS_OUTPUT_DIR, f"{prefix}.mp3")

    # 调用Edge TTS生成音频
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

    return output_file
