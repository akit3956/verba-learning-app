-- Supabase SQL for Teacher RAG
-- Run this in the Supabase SQL Editor

-- 1. Enable the pgvector extension
create extension if not exists vector;

-- 2. Create the embeddings table
create table if not exists teacher_embeddings (
  id bigserial primary key,
  content text not null,
  metadata jsonb,
  embedding vector(1536), -- For OpenAI text-embedding-3-small
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Create an HNSW index for faster vector search
create index on teacher_embeddings using hnsw (embedding vector_cosine_ops);

-- 4. Create a function to search for teacher notes (for the API)
create or replace function match_teacher_notes (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    teacher_embeddings.id,
    teacher_embeddings.content,
    teacher_embeddings.metadata,
    1 - (teacher_embeddings.embedding <=> query_embedding) as similarity
  from teacher_embeddings
  where 1 - (teacher_embeddings.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
$$;
