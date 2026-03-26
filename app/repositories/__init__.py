"""
Repositorios do Ebook Creator.

Re-exporta todas as classes de repositorio para facilitar imports:
    from app.repositories import BaseRepository, UserRepository

O Repository Pattern centraliza o acesso ao banco de dados.
Cada entidade tem seu repositorio com operacoes especificas,
e todos herdam do BaseRepository que fornece CRUD generico.
"""

from app.repositories.base import BaseRepository
from app.repositories.user_repo import UserRepository

__all__ = ["BaseRepository", "UserRepository"]
