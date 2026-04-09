-- SQL Script to set up the Supabase database for AI Copilot
-- Run this in the SQL Editor on your Supabase dashboard (https://supabase.com/dashboard/project/_/sql)

-- 1. Create the 'documents' table to track uploaded files
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- 3. Create a policy to allow all actions for the service_role key
-- (The service_role key bypasses RLS by default, but this adds flexibility)
CREATE POLICY "Allow all actions for authenticated users" 
ON public.documents 
FOR ALL 
TO authenticated 
USING (true);

-- 4. (Optional) Example for other tables if needed in the future
-- CREATE TABLE IF NOT EXISTS public.chat_sessions ( ... );
