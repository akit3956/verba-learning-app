-- 1. Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_embeddings ENABLE ROW LEVEL SECURITY;

-- 2. USERS Table Policies
-- Allow users to see their own profile (UUID matching auth.uid())
CREATE POLICY "Users can view their own profile" 
ON users FOR SELECT 
USING (id = auth.uid()::text);

-- Allow users to update their own profile
CREATE POLICY "Users can update their own profile" 
ON users FOR UPDATE 
USING (id = auth.uid()::text)
WITH CHECK (id = auth.uid()::text);

-- 3. TRANSACTIONS Table Policies
-- Allow users to view their own transaction history
CREATE POLICY "Users can view their own transactions" 
ON transactions FOR SELECT 
USING (user_id = auth.uid()::text);

-- 4. PASSWORD_RESET_TOKENS Table Policies
-- Allow users to view their own reset tokens (usually for verify logic)
CREATE POLICY "Users can view their own reset tokens" 
ON password_reset_tokens FOR SELECT 
USING (user_id = auth.uid()::text);

-- 5. TEACHER_EMBEDDINGS Table Policies
-- Allow all authenticated users (students) to READ teacher notes for RAG/Tutoring
CREATE POLICY "Students can read teacher notes" 
ON teacher_embeddings FOR SELECT 
TO authenticated 
USING (true);

-- 6. SETTINGS Table Policies
-- CRITICAL: By default, enabling RLS and NOT adding any policies for 'authenticated' or 'anon' 
-- effectively makes this table PRIVATE to the Service Role only.
-- This protects your OpenAI/Gemini API keys from being leaked to the frontend/public.

-- (Optional) If you want teachers to see settings, add a policy here, 
-- but for now, we leave it strictly private as requested.
