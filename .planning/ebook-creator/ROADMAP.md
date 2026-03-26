# Roadmap: Ebook Creator

## Overview

Construir um backend completo de Ebook Creator em 6 fases incrementais, mapeadas para 10 aulas. Cada fase adiciona uma camada arquitetural ao projeto, partindo de OOP puro ate uma API completa com interface visual. A abordagem bottom-up garante que o Joao entenda o "porque" de cada camada antes de usa-la.

## Phases

- [x] **Phase 1: Foundation** - OOP, estrutura do projeto, modelos SQLAlchemy e banco (Aulas 1-2)
- [ ] **Phase 2: Data Access** - Repository pattern e operacoes CRUD (Aula 3)
- [ ] **Phase 3: Authentication** - Auth service, JWT, hashing de senhas (Aula 4)
- [ ] **Phase 4: API Layer** - FastAPI endpoints, schemas Pydantic, CRUD via API (Aulas 5-6)
- [ ] **Phase 5: Features** - Servico de IA simulada e exportacao PDF (Aulas 7-8)
- [ ] **Phase 6: Integration & Frontend** - Fluxo end-to-end e interface Streamlit (Aulas 9-10)

## Phase Details

### Phase 1: Foundation
**Goal**: Estrutura do projeto criada, classes OOP definidas, modelos SQLAlchemy mapeados no PostgreSQL com Alembic
**Depends on**: Nothing (first phase)
**Aulas**: 1 e 2
**Plans**: 3 plans

Plans:
- [x] 01-01: Setup do projeto (uv, estrutura de pastas, dependencias) + classes OOP puras
- [x] 01-02: Modelos SQLAlchemy (User, Project, Chapter) com relacionamentos
- [x] 01-03: Configuracao do banco (SQLite/PostgreSQL) + Alembic migrations

### Phase 2: Data Access
**Goal**: Camada de repositorio completa com CRUD para todas as entidades
**Depends on**: Phase 1
**Aulas**: 3
**Plans**: 2 plans

Plans:
- [x] 02-01: Repository pattern base + UserRepository com CRUD
- [ ] 02-02: ProjectRepository e ChapterRepository com queries e filtros

### Phase 3: Authentication
**Goal**: Sistema de autenticacao funcional com registro, login, verificacao JWT e logout
**Depends on**: Phase 2
**Aulas**: 4
**Plans**: 2 plans

Plans:
- [ ] 03-01: Security module (bcrypt hashing, JWT encode/decode, config)
- [ ] 03-02: Auth service (register, login, verify token, logout)

### Phase 4: API Layer
**Goal**: FastAPI rodando com endpoints de auth e CRUD completo protegido por JWT
**Depends on**: Phase 3
**Aulas**: 5 e 6
**Plans**: 3 plans

Plans:
- [ ] 04-01: FastAPI setup + Pydantic schemas + endpoints de auth
- [ ] 04-02: Endpoints CRUD de Projects (protegidos por auth)
- [ ] 04-03: Endpoints CRUD de Chapters + dependency injection de usuario

### Phase 5: Features
**Goal**: Servico de IA simulada gerando texto e exportacao de ebook em PDF
**Depends on**: Phase 4
**Aulas**: 7 e 8
**Plans**: 2 plans

Plans:
- [ ] 05-01: AI service com Strategy pattern (interface + implementacao simulada)
- [ ] 05-02: Export service com geracao de PDF (ReportLab Platypus)

### Phase 6: Integration & Frontend
**Goal**: Fluxo completo end-to-end funcionando + interface Streamlit consumindo a API
**Depends on**: Phase 5
**Aulas**: 9 e 10
**Plans**: 2 plans

Plans:
- [ ] 06-01: Integracao end-to-end, tratamento de erros, validacoes de negocio
- [ ] 06-02: Interface Streamlit (login, projetos, editor, exportacao)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete | 2026-03-25 |
| 2. Data Access | 1/2 | In progress | - |
| 3. Authentication | 0/2 | Not started | - |
| 4. API Layer | 0/3 | Not started | - |
| 5. Features | 0/2 | Not started | - |
| 6. Integration & Frontend | 0/2 | Not started | - |
