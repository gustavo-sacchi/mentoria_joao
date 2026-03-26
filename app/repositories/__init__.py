"""
Repositorios do Ebook Creator.

Re-exporta as classes de repositorio para facilitar imports:
    from app.repositories import UserRepository

O Repository Pattern centraliza o acesso ao banco de dados.
Cada entidade tem seu repositorio com todas as operacoes de banco
(CRUD + queries especificas) em um unico lugar.
"""

from app.repositories.user_repo import UserRepository

__all__ = ["UserRepository"]
