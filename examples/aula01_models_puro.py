"""
Aula 01 - Classes de dominio OOP puras (dataclasses)

Este arquivo preserva as classes originais da Aula 1, ANTES da conversao
para SQLAlchemy. Serve como referencia para entender a evolucao:

    dataclass (aqui) -> SQLAlchemy Model (app/models/)

Conceitos demonstrados:
- dataclass com slots=True
- Type hints modernos (int | None)
- Metodo __post_init__ para validacao
- Metodo __repr__ customizado
- Property (metodo que parece atributo)
- Enum (conjunto fixo de valores)
- Metodos que alteram estado do objeto
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum


# ========================================
# ProjectStatus (Enum)
# ========================================

class ProjectStatus(Enum):
    """Status possiveis de um projeto de ebook.

    Usar Enum garante que o status so pode ser um destes valores.
    Tentar usar um valor invalido gera erro - muito melhor que string livre!
    """

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ========================================
# User (dataclass)
# ========================================

@dataclass(slots=True)
class User:
    """Representa um usuario do sistema de ebooks.

    Atributos:
        id: Identificador unico (None quando ainda nao foi salvo no banco)
        email: Email do usuario (deve conter @)
        name: Nome completo do usuario
        hashed_password: Senha ja criptografada (nunca armazene senha em texto!)
        created_at: Data/hora de criacao da conta
        is_active: Se o usuario esta ativo no sistema
    """

    id: int | None
    email: str
    name: str
    hashed_password: str
    created_at: datetime
    is_active: bool = True

    def __post_init__(self) -> None:
        """Validacao que roda automaticamente apos o __init__."""
        if not self.email:
            raise ValueError("Email nao pode ser vazio")
        if not self.name:
            raise ValueError("Nome nao pode ser vazio")

    def __repr__(self) -> str:
        """Representacao do objeto para debug. Nunca mostra a senha!"""
        return f"User(id={self.id}, email='{self.email}', name='{self.name}')"

    @property
    def is_valid_email(self) -> bool:
        """Verifica se o email contem @ (validacao simples)."""
        return "@" in self.email


# ========================================
# Project (dataclass)
# ========================================

@dataclass(slots=True)
class Project:
    """Representa um projeto de ebook no sistema.

    Um projeto pertence a um usuario (user_id) e contem capitulos.
    O fluxo normal e: DRAFT -> IN_PROGRESS -> COMPLETED
    """

    id: int | None
    user_id: int
    title: str
    created_at: datetime
    description: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    updated_at: datetime | None = None

    def mark_in_progress(self) -> None:
        """Marca o projeto como 'em andamento'."""
        self.status = ProjectStatus.IN_PROGRESS
        self.updated_at = datetime.now(UTC)

    def mark_completed(self) -> None:
        """Marca o projeto como concluido."""
        self.status = ProjectStatus.COMPLETED
        self.updated_at = datetime.now(UTC)


# ========================================
# Chapter (dataclass)
# ========================================

@dataclass(slots=True)
class Chapter:
    """Representa um capitulo dentro de um projeto de ebook."""

    id: int | None
    project_id: int
    title: str
    created_at: datetime
    content: str = ""
    order: int = 0
    ai_generated: bool = False
    updated_at: datetime | None = None

    def update_content(self, new_content: str, from_ai: bool = False) -> None:
        """Atualiza o conteudo do capitulo."""
        self.content = new_content
        self.ai_generated = from_ai
        self.updated_at = datetime.now(UTC)

    @property
    def word_count(self) -> int:
        """Conta o numero de palavras no conteudo."""
        if not self.content:
            return 0
        return len(self.content.split())
