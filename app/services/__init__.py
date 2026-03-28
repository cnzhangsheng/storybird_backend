"""Service layer dependency injection."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.reading_service import ReadingService


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    """获取 AuthService 实例。"""
    return AuthService(db)


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    """获取 UserService 实例。"""
    return UserService(db)


def get_book_service(db: Annotated[Session, Depends(get_db)]) -> BookService:
    """获取 BookService 实例。"""
    return BookService(db)


def get_reading_service(db: Annotated[Session, Depends(get_db)]) -> ReadingService:
    """获取 ReadingService 实例。"""
    return ReadingService(db)