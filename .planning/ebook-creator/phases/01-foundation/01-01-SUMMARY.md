# Phase 1 Plan 1: Setup do Projeto e Classes OOP Puras - Summary

**Estrutura de pastas criada, dependencias instaladas e 3 classes de dominio OOP puras implementadas com dataclasses para ensinar OOP antes de SQLAlchemy.**

## Accomplishments
- Instaladas 12 dependencias do projeto via `uv add` (FastAPI, SQLAlchemy, Alembic, JWT, bcrypt, Pydantic, etc.)
- Criada estrutura completa de pastas seguindo o DESIGN.md (app/models, repositories, services, routes, schemas, core)
- Implementadas 3 classes de dominio com dataclasses: User, Project, Chapter
- Criado Enum ProjectStatus com 3 estados (DRAFT, IN_PROGRESS, COMPLETED)
- Criado script de demonstracao didatico com 5 secoes para uso na Aula 01

## Files Created/Modified
- `pyproject.toml` - Adicionadas dependencias e build-system (hatchling) para tornar o pacote `app` importavel
- `app/__init__.py` - Pacote raiz da aplicacao
- `app/models/__init__.py` - Re-exporta User, Project, ProjectStatus, Chapter
- `app/models/user.py` - Classe User com dataclass, validacao no __post_init__, property is_valid_email
- `app/models/project.py` - Classe Project com Enum ProjectStatus, metodos mark_in_progress/mark_completed
- `app/models/chapter.py` - Classe Chapter com metodo update_content, property word_count
- `app/repositories/__init__.py` - Pacote vazio (sera usado na Phase 2)
- `app/services/__init__.py` - Pacote vazio (sera usado na Phase 3)
- `app/routes/__init__.py` - Pacote vazio (sera usado na Phase 4)
- `app/schemas/__init__.py` - Pacote vazio (sera usado na Phase 4)
- `app/core/__init__.py` - Pacote vazio (sera usado na Phase 1.3)
- `examples/aula01_oop_demo.py` - Script de demonstracao com 5 secoes didaticas

## Decisions Made
- Adicionado `[build-system]` com hatchling ao pyproject.toml para que `uv` instale o pacote `app` como modulo importavel. Sem isso, scripts em `examples/` nao conseguem importar `from app.models import ...`. Isso e necessario para o fluxo pedagogico de rodar exemplos a partir de qualquer diretorio.
- Strings no demo script usam apenas ASCII para evitar problemas de encoding no terminal Windows.

## Deviations from Plan
- Adicionado `[build-system]` e `[tool.hatch.build.targets.wheel]` ao pyproject.toml (nao previsto no plano). Necessario para resolver `ModuleNotFoundError` ao rodar scripts em `examples/`. Bug auto-corrigido conforme Deviation Rule 1.

## Issues Encountered
- `ModuleNotFoundError: No module named 'app'` ao rodar `uv run python examples/aula01_oop_demo.py`. Resolvido adicionando build-system com hatchling ao pyproject.toml e executando `uv sync`.
- Caractere acentuado ("versatil") exibido incorretamente no terminal Windows. Resolvido substituindo por versao sem acento.

## Next Phase Readiness
- Estrutura de pastas completa e pronta para receber modelos SQLAlchemy (Plan 01-02)
- Classes de dominio servem como referencia para mapear para tabelas do banco
- Todas as dependencias (SQLAlchemy, Alembic, psycopg2-binary) ja instaladas

---
*Phase: 01-foundation*
*Completed: 2026-02-12*
