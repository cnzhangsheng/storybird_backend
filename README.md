# Storycoe Backend - 绘本创后端服务

**自己做绘本，逐句跟读练口语**

## 简介

Storycoe（绘本创）后端服务，为 Flutter 应用提供 API 支持。

## 功能特性

- 🔐 用户认证（手机验证码登录）
- 📚 绘本管理（创建、更新、删除）
- 🖼️ 图片上传与处理
- 🤖 AI 绘本生成（Google Gemini）
- 👁️ OCR 图片识别
- 📖 阅读进度追踪

## 技术栈

- **框架**：FastAPI
- **数据库**：PostgreSQL + SQLAlchemy
- **认证**：JWT
- **AI**：Google Gemini AI / Google Cloud Vision

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 运行服务
python run.py
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc