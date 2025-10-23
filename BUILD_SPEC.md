# Andromeda — Build Specification (Agentic AI Second Brain)

This document outlines a practical, phased plan to build Andromeda: a second-brain knowledge system combining Notion-like templates, Obsidian-style graph links, and AI-powered organization.

## Goals
- Notes are "stars" in a personal galaxy.
- Links between notes form constellations.
- Templates accelerate note creation.
- AI (NLP, embeddings, summarization, speech-to-text) augments discovery and automation.

## High-level architecture
- Backend: Django (current) exposing REST + GraphQL endpoints for notes, templates, links, attachments, and tasks.
- Frontend: Tailwind-based UI, HTMX for progressive enhancement, Alpine.js for micro-interactions; optional React for complex flows.
- Storage: PostgreSQL for production; SQLite for local dev. Attachments via S3-compatible storage.
- Vector store: PostgreSQL with pgvector, or external vector DB (Pinecone, Milvus, Weaviate).
- AI: OpenAI/GPT for text generation, local embedding models with Hugging Face or sentence-transformers; optional self-hosted LLMs.

## Data model (summary)
- User (custom)
- Note (UUID, owner, title, body, metadata JSON, embedding_id)
- Template (owner, name, JSON content)
- Link (src, dst, kind)
- Attachment (file, mime, title)
- APIIntegration (config JSON)
- AITask (type, status, result)

## Key APIs
- CRUD for notes/templates/links/attachments
- Search: hybrid (keyword + vector search)
- AI endpoints: /api/embed, /api/summarize, /api/transcribe
- Webhooks for background tasks

## UI/UX
- Landing: immersive hero, onboarding CTAs
- App layout: left navigation (collapsed), central canvas/grid of stars, right panel for details
- Note editor: blocks-based editor with markdown and atomic blocks
- Graph view: interactive force graph linking stars

## Background processing
- Celery + Redis for task queue
- Workers for embedding, transcription, OCR, summarization

## Security & privacy
- Per-user encryption for sensitive fields
- RBAC for teams
- Audit logs, rate limiting, secure storage of API keys

## Phase 1 (MVP)
- Auth, note CRUD, templates, basic links
- Simple UI with hero + note grid, note detail page
- Embedding pipeline (on-demand) and basic search

## Phase 2
- Background workers, scheduled tasks
- Graph visualization UI and link suggestions
- Summarization & Q/A on note corpus

## Phase 3
- Team features, sharing permissions
- Rich integrations (GDrive, Notion import)
- Offline sync, mobile improvements

## Ops & infra
- Dockerized services for web, workers, Redis, Postgres, vector DB
- CI/CD, migrations, backups

## Roadmap & milestones
1. Core data model & CRUD (2 weeks)
2. Embeddings & search (2 weeks)
3. Graph UI & link suggestions (3 weeks)
4. Summarization & Q/A (3 weeks)
5. Team & sharing features (4 weeks)

## Notes
This spec focuses on an incremental approach balancing quick wins (MVP) and long-term capabilities (graph + AI). Use this as a living doc; keep design decisions in a separate ADR record.
