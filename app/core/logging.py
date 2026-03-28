"""Logging configuration using loguru."""
import sys
from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """配置日志。

    Args:
        level: 日志级别，默认 INFO
    """
    # 移除默认处理器
    logger.remove()

    # 添加标准输出处理器
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 添加文件日志（可选，用于生产环境）
    # logger.add(
    #     "logs/app.log",
    #     level="DEBUG",
    #     rotation="10 MB",
    #     retention="7 days",
    #     compression="zip",
    # )


def get_logger():
    """获取 logger 实例。"""
    return logger