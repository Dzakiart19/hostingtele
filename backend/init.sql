-- Database initialization script for ZipHostBot
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum untuk status project
CREATE TYPE project_status AS ENUM ('PENDING', 'PROCESSING', 'RUNNING', 'STOPPED', 'FAILED');

-- Tabel users untuk menyimpan data pengguna dari Telegram
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    first_name TEXT NOT NULL,
    username TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabel projects untuk menyimpan informasi bot yang di-deploy
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status project_status DEFAULT 'PENDING',
    last_error_log TEXT,
    container_id TEXT,
    zip_storage_path TEXT,
    encrypted_bot_token TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index untuk performa query
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);

-- Trigger untuk update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();