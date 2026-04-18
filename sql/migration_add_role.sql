-- 迁移脚本: 添加用户角色字段
-- 执行日期: 2026-04-18
-- 说明: 添加 role 字段区分用户角色: 0=普通用户, 1=高级用户, 10=管理员

-- 添加 role 字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE users ADD COLUMN role INTEGER NOT NULL DEFAULT 0;
        COMMENT ON COLUMN users.role IS '用户角色: 0=普通用户, 1=高级用户, 10=管理员';
    END IF;
END $$;

-- 如果上面的 DO 块不工作，可以手动执行:
-- ALTER TABLE users ADD COLUMN role INTEGER NOT NULL DEFAULT 0;