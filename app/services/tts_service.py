"""TTS service using edge-tts for generating sentence audio."""
import asyncio
import tempfile
from pathlib import Path
from typing import Optional

import edge_tts
from loguru import logger

from app.core.config import settings


# 发音人和语速配置
VOICE_CONFIG = {
    "us": "en-US-AvaNeural",   # 美式女声
    "gb": "en-GB-SoniaNeural", # 英式女声
}

RATE_CONFIG = {
    "normal": "+0%",   # 正常语速
    "slow": "-30%",    # 慢速（降低 30%）
}


class TtsService:
    """TTS 服务 - 使用 edge-tts 生成句子音频。

    edge-tts 是 Microsoft Edge 的在线文本转语音服务，
    支持多种语言和发音人，无需 API Key。
    """

    def __init__(self):
        """初始化 TTS 服务."""
        self.upload_dir = Path(settings.upload_dir)

    async def generate_audio(
        self,
        text: str,
        accent: str = "us",
        speed: str = "normal",
    ) -> bytes:
        """生成单个音频文件.

        Args:
            text: 要转换的英文文本
            accent: 发音风格 ("us" 或 "gb")
            speed: 语速 ("normal" 或 "slow")

        Returns:
            音频文件字节数据 (MP3 格式)
        """
        if not text or not text.strip():
            logger.warning("TTS 文本为空，跳过生成")
            return b""

        voice = VOICE_CONFIG.get(accent, VOICE_CONFIG["us"])
        rate = RATE_CONFIG.get(speed, RATE_CONFIG["normal"])

        try:
            communicate = edge_tts.Communicate(
                text=text.strip(),
                voice=voice,
                rate=rate,
            )

            # 使用临时文件收集音频数据
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            await communicate.save(tmp_path)

            # 读取音频数据
            with open(tmp_path, "rb") as f:
                audio_data = f.read()

            # 清理临时文件
            Path(tmp_path).unlink(missing_ok=True)

            logger.info(f"TTS 生成成功: accent={accent}, speed={speed}, text='{text[:30]}...', size={len(audio_data)} bytes")
            return audio_data

        except Exception as e:
            logger.error(f"TTS 生成失败: text='{text[:30]}...', error={e}")
            raise

    async def generate_all_accents(
        self,
        text: str,
        book_id: int,
        sentence_id: int,
    ) -> dict[str, str]:
        """生成所有 4 种音频变体并保存.

        Args:
            text: 英文文本
            book_id: 书籍 ID
            sentence_id: 句子 ID

        Returns:
            音频 URL 字典 {
                "us_normal": "...",
                "us_slow": "...",
                "gb_normal": "...",
                "gb_slow": "...",
            }
        """
        if not text or not text.strip():
            return {
                "us_normal": None,
                "us_slow": None,
                "gb_normal": None,
                "gb_slow": None,
            }

        # 创建音频目录
        audio_dir = self.upload_dir / "books" / str(book_id) / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # 并行生成 4 种音频
        tasks = []
        configs = [
            ("us", "normal", f"{sentence_id}_us_normal.mp3"),
            ("us", "slow", f"{sentence_id}_us_slow.mp3"),
            ("gb", "normal", f"{sentence_id}_gb_normal.mp3"),
            ("gb", "slow", f"{sentence_id}_gb_slow.mp3"),
        ]

        for accent, speed, filename in configs:
            tasks.append(self._generate_and_save(text, accent, speed, audio_dir / filename))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 构建返回字典
        urls = {}
        keys = ["us_normal", "us_slow", "gb_normal", "gb_slow"]

        for i, (key, result) in enumerate(zip(keys, results)):
            if isinstance(result, Exception):
                logger.error(f"音频生成失败: {key}, error={result}")
                urls[key] = None
            elif result:
                urls[key] = f"/static/books/{book_id}/audio/{configs[i][2]}"
            else:
                urls[key] = None

        logger.info(f"句子音频生成完成: sentence_id={sentence_id}, urls={urls}")
        return urls

    async def _generate_and_save(
        self,
        text: str,
        accent: str,
        speed: str,
        filepath: Path,
    ) -> bool:
        """生成并保存单个音频文件.

        Args:
            text: 英文文本
            accent: 发音风格
            speed: 语速
            filepath: 保存路径

        Returns:
            是否成功
        """
        try:
            audio_data = await self.generate_audio(text, accent, speed)
            if not audio_data:
                return False

            with open(filepath, "wb") as f:
                f.write(audio_data)

            return True

        except Exception as e:
            logger.error(f"保存音频失败: filepath={filepath}, error={e}")
            return False


# 全局实例
tts_service = TtsService()