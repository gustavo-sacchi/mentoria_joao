"""
Modelo SQLAlchemy: Project (Projeto de Ebook)

ANTES (Aula 01): @dataclass com Enum para status e metodos de transicao.
AGORA (Aula 02): Modelo SQLAlchemy com ForeignKey apontando para User.

Conceitos ensinados:
- Enum: continua igual - conjunto fixo de valores possiveis
- ForeignKey: coluna que referencia outra tabela (user_id -> users.id)
- relationship(): acesso bidirecional (Project.owner <-> User.projects)
- onupdate=func.now(): banco atualiza automaticamente o timestamp
- Metodos de negocio preservados (mark_in_progress, mark_completed)
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# TYPE_CHECKING evita importacao circular em tempo de execucao
if TYPE_CHECKING:
    from app.models.chapter import Chapter
    from app.models.user import User


class ProjectStatus(Enum):
    """Status possiveis de um projeto de ebook.

    Usar Enum garante que o status so pode ser um destes valores.
    O .value de cada item e a string que sera salva no banco.

    Exemplo:
        ProjectStatus.DRAFT.value  ->  "draft"
        ProjectStatus("draft")     ->  ProjectStatus.DRAFT
    """

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Project(Base):
    """Modelo de projeto mapeado para a tabela 'projects' no banco.

    Relacionamentos:
    - Pertence a um User (via user_id -> users.id)
    - Tem varios Chapters (relacao 1:N)

    O status e armazenado como string no banco (String(20))
    em vez de usar o tipo Enum nativo do PostgreSQL, para simplicidade.
    """

    __tablename__ = "projects"

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True)

    # ForeignKey("users.id"): esta coluna referencia a tabela 'users', coluna 'id'.
    # Isso cria a relacao "um usuario tem muitos projetos" no banco de dados.
    # O banco garante que user_id sempre aponta para um usuario existente.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    title: Mapped[str] = mapped_column(String(200))

    # Text: coluna de texto sem limite de tamanho (TEXT no PostgreSQL)
    # default="": valor padrao definido pelo Python ao criar o objeto
    description: Mapped[str] = mapped_column(Text, default="")

    # Armazenamos o status como string (o .value do Enum).
    # Exemplo: ProjectStatus.DRAFT.value -> "draft"
    status: Mapped[str] = mapped_column(
        String(20),
        default=ProjectStatus.DRAFT.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # nullable=True: esta coluna pode ser NULL (None em Python).
    # onupdate=func.now(): o banco atualiza automaticamente quando o registro muda.
    # Mapped[datetime | None]: o tipo indica que pode ser None.
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # --- Relacionamentos ---
    # owner: acessa o usuario dono deste projeto (Project.owner -> User)
    # back_populates="projects": vincula com User.projects
    owner: Mapped[User] = relationship(
        "User",
        back_populates="projects",
    )

    # chapters: acessa os capitulos deste projeto (Project.chapters -> [Chapter])
    # cascade="all, delete-orphan": deletar o projeto deleta seus capitulos
    chapters: Mapped[list[Chapter]] = relationship(
        "Chapter",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # --- Metodos de Negocio ---
    # Preservamos os metodos da versao dataclass.
    # Modelos SQLAlchemy podem ter metodos normais alem das colunas!

    def mark_in_progress(self) -> None:
        """Marca o projeto como 'em andamento'.

        Encapsula a logica de mudanca de estado:
        - Muda o status para IN_PROGRESS
        - Atualiza o timestamp updated_at
        """
        self.status = ProjectStatus.IN_PROGRESS.value
        self.updated_at = datetime.now(UTC)

    def mark_completed(self) -> None:
        """Marca o projeto como concluido.

        Atualiza o status e registra quando foi finalizado.
        """
        self.status = ProjectStatus.COMPLETED.value
        self.updated_at = datetime.now(UTC)

    def __repr__(self) -> str:
        return f"Project(id={self.id}, title='{self.title}', status='{self.status}')"
