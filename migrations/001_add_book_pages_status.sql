-- Migration: Add status column to book_pages table
-- Date: 2026-04-10
-- Description: Support async OCR processing status for each page

-- Add status column if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'book_pages' AND column_name = 'status'
    ) THEN
        ALTER TABLE book_pages ADD COLUMN status VARCHAR(20) DEFAULT 'completed';
        COMMENT ON COLUMN book_pages.status IS 'processing, completed, error';
    END IF;
END $$;

-- Verify the column exists
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'book_pages' AND column_name = 'status';