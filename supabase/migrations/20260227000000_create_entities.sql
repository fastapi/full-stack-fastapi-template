-- supabase/migrations/20260227000000_create_entities.sql
-- Creates the entities table, owner index, updated_at trigger, and RLS policies.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    owner_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for owner-scoped queries
CREATE INDEX idx_entities_owner_id ON entities(owner_id);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER entities_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Row-Level Security
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their own entities
-- (service role key bypasses RLS for admin operations)
CREATE POLICY "Users can view own entities"
    ON entities FOR SELECT
    USING (owner_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can insert own entities"
    ON entities FOR INSERT
    WITH CHECK (owner_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can update own entities"
    ON entities FOR UPDATE
    USING (owner_id = current_setting('request.jwt.claim.sub', true))
    WITH CHECK (owner_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can delete own entities"
    ON entities FOR DELETE
    USING (owner_id = current_setting('request.jwt.claim.sub', true));
