"""API routes package."""
from app.api.auth import router as auth_router
from app.api.books import router as books_router
from app.api.users import router as users_router
from app.api.reading import router as reading_router
from app.api.ocr import router as ocr_router
from app.api.generate import router as generate_router

__all__ = ["auth_router", "books_router", "users_router", "reading_router", "ocr_router", "generate_router"]