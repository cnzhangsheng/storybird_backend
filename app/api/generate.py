"""API routes for book generation."""
import asyncio
import base64
import traceback
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import MessageResponse
from app.services.file_storage_service import file_storage
from app.services.ocr_service import ocr_service, OcrSentence
from app.models.db_models import Book, BookPage, Sentence

router = APIRouter(prefix="/generate", tags=["Book Generation"])


@router.post("/book")
async def generate_book(
    title: str = Form(...),
    cover: UploadFile = File(None),
    images: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成朗读绘本（带进度）。

    Args:
        title: 绘本标题
        cover: 封面图片（可选，单张）
        images: 上传的图片列表
        current_user: 当前用户
        db: 数据库会话

    Returns:
        StreamingResponse 带进度的响应
    """
    user_id = current_user["id"]
    logger.info(f"开始生成绘本: user_id={user_id}, title={title}, images_count={len(images)}, has_cover={cover is not None and cover.filename}")

    async def generate_with_progress():
        """生成绘本并发送进度。"""
        total_steps = len(images) + 2  # 图片数 + 创建书籍 + 完成
        current_step = 0

        def progress_message(step: int, message: str, data: dict = None):
            """生成进度消息。"""
            import json
            progress = int((step / total_steps) * 100)
            result = {
                "step": step,
                "total": total_steps,
                "progress": progress,
                "message": message,
            }
            if data:
                result["data"] = data
            return f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

        try:
            # 步骤1: 创建书籍记录
            yield progress_message(current_step, "正在创建绘本...")

            book = Book(
                user_id=user_id,
                title=title,
                level=1,
                status="generating",
                is_new=True,
            )
            db.add(book)
            db.flush()  # 获取 book_id
            book_id = str(book.id)
            logger.info(f"创建书籍记录: book_id={book_id}")

            # 创建书籍目录
            try:
                file_storage.create_book_dir(book_id)
                logger.info(f"创建书籍目录成功: book_id={book_id}")
            except Exception as e:
                logger.error(f"创建书籍目录失败: book_id={book_id}, error={e}")
                raise

            # 保存封面图片
            cover_url = None
            if cover and cover.filename:
                try:
                    cover_data = await cover.read()
                    logger.debug(f"读取封面数据: size={len(cover_data)}")
                    cover_path = file_storage.save_cover_image(
                        book_id=book_id,
                        image_data=cover_data,
                    )
                    cover_url = f"/static/{cover_path}"
                    book.cover_image = cover_url
                    logger.info(f"保存封面成功: book_id={book_id}, cover_url={cover_url}")
                except Exception as e:
                    logger.error(f"保存封面失败: book_id={book_id}, error={e}")
                    # 封面失败不影响整体流程

            current_step += 1
            yield progress_message(current_step, f"已创建绘本: {title}")

            # 步骤2: 读取并保存所有图片
            page_data_list = []  # 存储 (page, image_data) 用于后续 OCR

            for i, image_file in enumerate(images):
                try:
                    # 读取图片数据
                    image_data = await image_file.read()
                    logger.debug(f"读取图片 {i+1}: size={len(image_data)}, filename={image_file.filename}")

                    if not image_data:
                        logger.warning(f"图片 {i+1} 数据为空，跳过")
                        continue

                    # 保存图片到文件系统
                    relative_path = file_storage.save_page_image(
                        book_id=book_id,
                        page_number=i + 1,
                        image_data=image_data,
                    )
                    image_url = f"/static/{relative_path}"

                    # 创建页面记录
                    page = BookPage(
                        book_id=book.id,
                        page_number=i + 1,
                        image_url=image_url,
                    )
                    db.add(page)
                    db.flush()

                    page_data_list.append((page, image_data))
                    logger.debug(f"保存图片 {i+1} 成功: {relative_path}")
                except Exception as e:
                    logger.error(f"保存图片 {i+1} 失败: {e}")
                    import json
                    yield f"data: {json.dumps({'error': f'保存图片 {i+1} 失败: {str(e)}'}, ensure_ascii=False)}\n\n"
                    return

            if not page_data_list:
                logger.error("没有有效的图片数据")
                import json
                yield f"data: {json.dumps({'error': '没有有效的图片数据'}, ensure_ascii=False)}\n\n"
                return

            current_step += 1
            yield progress_message(current_step, f"正在识别 {len(page_data_list)} 张图片中的文字...")

            # 步骤3: 并行 OCR 识别所有图片
            logger.info(f"开始并行 OCR 识别: book_id={book_id}, pages={len(page_data_list)}")

            ocr_tasks = [
                ocr_service.recognize_image(image_data)
                for _, image_data in page_data_list
            ]
            ocr_results: List[List[OcrSentence]] = await asyncio.gather(*ocr_tasks)

            # 步骤4: 保存所有句子
            for idx, (page, _) in enumerate(page_data_list):
                sentences = ocr_results[idx]
                for j, sentence in enumerate(sentences):
                    sentence_record = Sentence(
                        page_id=page.id,
                        sentence_order=j + 1,
                        en=sentence.en,
                        zh=sentence.zh,
                    )
                    db.add(sentence_record)

            db.commit()

            current_step += 1
            yield progress_message(
                current_step,
                f"已完成文字识别，共处理 {len(page_data_list)} 张图片",
            )

            # 步骤5: 完成
            book.status = "completed"
            book.has_audio = True
            db.commit()

            yield progress_message(
                total_steps,
                "绘本生成完成！",
                {
                    "book_id": book_id,
                    "title": title,
                    "total_pages": len(page_data_list),
                }
            )

            logger.info(f"绘本生成完成: book_id={book_id}, pages={len(page_data_list)}")

        except Exception as e:
            logger.error(f"生成绘本失败: {e}\n{traceback.format_exc()}")
            import json
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_with_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )