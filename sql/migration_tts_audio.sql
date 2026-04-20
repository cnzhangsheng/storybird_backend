-- Migration: Add TTS audio fields to sentences table
-- Date: 2026-04-20
-- Description: 为每个句子添加 4 种 TTS 音频字段（美式/英式，正常/慢速）

-- 删除旧的 audio_url 字段
ALTER TABLE sentences DROP COLUMN IF EXISTS audio_url;

-- 添加新的 TTS 音频字段
ALTER TABLE sentences ADD COLUMN IF NOT EXISTS audio_us_normal VARCHAR(500);
ALTER TABLE sentences ADD COLUMN IF NOT EXISTS audio_us_slow VARCHAR(500);
ALTER TABLE sentences ADD COLUMN IF NOT EXISTS audio_gb_normal VARCHAR(500);
ALTER TABLE sentences ADD COLUMN IF NOT EXISTS audio_gb_slow VARCHAR(500);

-- 注释
COMMENT ON COLUMN sentences.audio_us_normal IS '美式英语正常语速音频 URL';
COMMENT ON COLUMN sentences.audio_us_slow IS '美式英语慢速音频 URL';
COMMENT ON COLUMN sentences.audio_gb_normal IS '英式英语正常语速音频 URL';
COMMENT ON COLUMN sentences.audio_gb_slow IS '英式英语慢速音频 URL';