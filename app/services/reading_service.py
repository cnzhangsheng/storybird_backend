"""Reading progress service using SQLAlchemy."""
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.schemas import ReadingProgressUpdate, ReadingProgressResponse, MessageResponse
from app.models.db_models import User, Book, ReadingProgress


def utcnow():
    """返回 UTC 时区的当前时间。"""
    return datetime.now(timezone.utc)


class ReadingService:
    """阅读进度服务类。

    封装所有阅读进度相关的业务逻辑和数据库操作。
    """

    def __init__(self, db: Session):
        """初始化服务。

        Args:
            db: SQLAlchemy 数据库会话
        """
        self.db = db

    def get_reading_progress(self, user_id: str, book_id: str) -> ReadingProgressResponse:
        """获取阅读进度。

        Args:
            user_id: 用户 ID
            book_id: 书籍 ID

        Returns:
            阅读进度数据
        """
        progress = self.db.query(ReadingProgress).filter(
            ReadingProgress.user_id == user_id,
            ReadingProgress.book_id == book_id,
        ).first()

        if not progress:
            # 返回默认进度
            logger.debug(f"阅读进度不存在，返回默认: user_id={user_id}, book_id={book_id}")
            return ReadingProgressResponse(
                id=None,
                user_id=user_id,
                book_id=book_id,
                current_page=0,
                total_pages=0,
                completed=False,
                last_read_at=utcnow(),
                created_at=utcnow(),
                updated_at=utcnow(),
            )

        return ReadingProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            book_id=progress.book_id,
            current_page=progress.current_page,
            total_pages=progress.total_pages,
            completed=progress.completed,
            last_read_at=progress.last_read_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at,
        )

    def update_reading_progress(
        self,
        user_id: str,
        book_id: str,
        update_data: ReadingProgressUpdate,
        current_books_read: int,
    ) -> ReadingProgressResponse:
        """更新阅读进度。

        Args:
            user_id: 用户 ID
            book_id: 书籍 ID
            update_data: 更新数据
            current_books_read: 当前已读书籍数

        Returns:
            更新后的阅读进度
        """
        progress = self.db.query(ReadingProgress).filter(
            ReadingProgress.user_id == user_id,
            ReadingProgress.book_id == book_id,
        ).first()

        now = utcnow()

        if progress:
            # 更新已有进度
            if update_data.current_page is not None:
                progress.current_page = update_data.current_page
            if update_data.completed is not None:
                progress.completed = update_data.completed
            progress.last_read_at = now
            logger.info(f"更新阅读进度: user_id={user_id}, book_id={book_id}")
        else:
            # 创建新进度
            progress = ReadingProgress(
                user_id=user_id,
                book_id=book_id,
                current_page=update_data.current_page or 0,
                completed=update_data.completed or False,
                last_read_at=now,
            )
            self.db.add(progress)
            logger.info(f"创建阅读进度: user_id={user_id}, book_id={book_id}")

            # 标记书籍为已读（非新书）
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if book:
                book.is_new = False

        self.db.commit()
        self.db.refresh(progress)

        # 如果完成阅读，更新用户统计
        if update_data.completed:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.books_read = current_books_read + 1
                self.db.commit()
                logger.info(f"完成阅读，更新用户统计: user_id={user_id}")

        return ReadingProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            book_id=progress.book_id,
            current_page=progress.current_page,
            total_pages=progress.total_pages,
            completed=progress.completed,
            last_read_at=progress.last_read_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at,
        )

    def mark_book_completed(self, user_id: str, book_id: str, current_books_read: int) -> MessageResponse:
        """标记书籍为已完成。

        Args:
            user_id: 用户 ID
            book_id: 书籍 ID
            current_books_read: 当前已读书籍数

        Returns:
            成功消息

        Raises:
            NotFoundException: 书籍不存在
        """
        # 校验书籍存在性和权限
        book = self.db.query(Book).filter(Book.id == book_id, Book.user_id == user_id).first()

        if not book:
            logger.warning(f"书籍不存在或无权限: book_id={book_id}, user_id={user_id}")
            raise NotFoundException(message="书籍未找到")

        # 更新或创建进度
        progress = self.db.query(ReadingProgress).filter(
            ReadingProgress.user_id == user_id,
            ReadingProgress.book_id == book_id,
        ).first()

        now = utcnow()

        if progress:
            progress.completed = True
            progress.last_read_at = now
        else:
            progress = ReadingProgress(
                user_id=user_id,
                book_id=book_id,
                completed=True,
                current_page=0,
                total_pages=0,
                last_read_at=now,
            )
            self.db.add(progress)

        # 更新用户统计
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.books_read = current_books_read + 1

        # 标记书籍为非新书
        book.is_new = False

        self.db.commit()
        logger.info(f"标记书籍完成: user_id={user_id}, book_id={book_id}")

        return MessageResponse(message="恭喜完成阅读！")