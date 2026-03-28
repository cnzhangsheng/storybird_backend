"""OCR API routes for text recognition."""
import re
from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException
from loguru import logger

from app.models.schemas import MessageResponse

router = APIRouter(prefix="/ocr", tags=["OCR"])

# 是否启用 Google Vision API（如果未配置则使用模拟数据）
USE_MOCK = True  # 设为 False 以启用真实 OCR


def split_into_sentences(text: str) -> List[str]:
    """将文本按句子分割。

    根据英文句式（以 . ! ? 结尾）自动分句。
    """
    # 移除多余的空白字符
    text = ' '.join(text.split())

    # 使用正则表达式按句子分割
    # 匹配以 . ! ? 结尾的句子
    pattern = r'[^.!?]*[.!?]'
    matches = re.findall(pattern, text)

    # 过滤空句子并清理
    sentences = []
    for match in matches:
        sentence = match.strip()
        if sentence and len(sentence) > 1:
            sentences.append(sentence)

    # 如果没有找到句子分隔符，将整个文本作为一个句子
    if not sentences and text.strip():
        sentences.append(text.strip())

    return sentences


async def recognize_with_google_vision(image_bytes: bytes) -> List[str]:
    """使用 Google Vision API 识别图片中的英文文字。

    Args:
        image_bytes: 图片字节数据

    Returns:
        识别的句子列表
    """
    try:
        from google.cloud import vision

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)

        # 执行文字识别
        response = client.text_detection(image=image)

        if response.error.message:
            logger.error(f"Google Vision API error: {response.error.message}")
            raise Exception(response.error.message)

        # 获取识别的文字
        texts = response.text_annotations
        if not texts:
            return []

        # 第一个结果是完整的识别文本
        full_text = texts[0].description

        # 按句子分割
        sentences = split_into_sentences(full_text)

        logger.info(f"OCR recognized {len(sentences)} sentences")
        return sentences

    except ImportError:
        logger.warning("google-cloud-vision not installed, using mock data")
        raise Exception("Google Vision API not available")
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise


def get_mock_sentences() -> List[dict]:
    """返回模拟的 OCR 识别结果（用于开发和测试）。"""
    return [
        {"en": "Once upon a time, there was a little bird.", "zh": "从前，有一只小鸟。"},
        {"en": "She lived in a big, green forest.", "zh": "她住在一个大大的绿色森林里。"},
        {"en": "One sunny morning, she decided to fly away.", "zh": "一个阳光明媚的早晨，她决定飞走。"},
        {"en": "Where will she go?", "zh": "她会去哪里呢？"},
        {"en": "The adventure begins!", "zh": "冒险开始了！"},
    ]


@router.post("/recognize")
async def recognize_text(file: UploadFile = File(...)):
    """识别图片中的英文文字。

    Args:
        file: 上传的图片文件

    Returns:
        识别的句子列表
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="请上传图片文件",
        )

    try:
        # 读取图片数据
        image_bytes = await file.read()
        logger.info(f"Received image: {file.filename}, size: {len(image_bytes)} bytes")

        if USE_MOCK:
            # 使用模拟数据
            logger.info("Using mock OCR data")
            sentences = get_mock_sentences()
        else:
            # 使用 Google Vision API
            recognized = await recognize_with_google_vision(image_bytes)
            sentences = [{"en": s, "zh": ""} for s in recognized]

        if not sentences:
            return {
                "success": False,
                "message": "未能识别到英文文字，请上传清晰的英文绘本照片",
                "sentences": [],
            }

        return {
            "success": True,
            "message": f"识别成功，共 {len(sentences)} 个句子",
            "sentences": sentences,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"识别失败: {str(e)}",
        )