"""
Repositorios do Ebook Creator.

Re-exporta as classes de repositorio para facilitar imports:
    from app.repositories import UserRepository, ProjectRepository, ChapterRepository

O Repository Pattern centraliza o acesso ao banco de dados.
Cada entidade tem seu repositorio com todas as operacoes de banco
(CRUD + queries especificas) em um unico lugar.

Cada repositorio e autocontido: inclui as operacoes CRUD basicas
(get_by_id, get_all, create, update, delete, count) alem de
queries especificas da entidade. Isso torna cada arquivo
independente e facil de entender.
"""

from app.repositories.chapter_repo import ChapterRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.user_repo import UserRepository

__all__ = ["UserRepository", "ProjectRepository", "ChapterRepository"]
