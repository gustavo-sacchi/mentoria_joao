"""
Modelo SQLAlchemy: Chapter (Capitulo de Ebook)

ANTES (Aula 01): @dataclass com metodo update_content() e property word_count.
AGORA (Aula 02): Modelo SQLAlchemy com ForeignKey apontando para Project.

Conceitos ensinados:
- ForeignKey para segundo nivel de relacao (Chapter -> Project -> User)
- Metodos e properties preservados no modelo SQLAlchemy
- Text vs String: quando usar cada tipo de coluna
- default vs server_default: quem define o valor (Python vs banco)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# TYPE_CHECKING evita importacao circular em tempo de execucao
if TYPE_CHECKING:
    from app.models.project import Project


class Chapter(Base):
    """Modelo de capitulo mapeado para a tabela 'chapters' no banco.

    Relacionamentos:
    - Pertence a um Project (via project_id -> projects.id)

    Metodos preservados da versao dataclass:
    - update_content(): atualiza texto e marca se veio de IA
    - word_count: property que conta palavras do conteudo
    """

    __tablename__ = "chapters"

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True)

    # ForeignKey("projects.id"): referencia a tabela 'projects'
    # Um capitulo SEMPRE pertence a um projeto
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    title: Mapped[str] = mapped_column(String(200))

    # Text: tipo sem limite de tamanho, ideal para conteudo longo
    # default="": capitulo comeca sem conteudo
    content: Mapped[str] = mapped_column(Text, default="")

    # order: posicao do capitulo no ebook (0 = primeiro)
    order: Mapped[int] = mapped_column(default=0)

    # ai_generated: flag que indica se o conteudo foi gerado por IA
    ai_generated: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # --- Relacionamentos ---
    # project: acessa o projeto ao qual este capitulo pertence
    # back_populates="chapters": vincula com Project.chapters
    project: Mapped[Project] = relationship(
        "Project",
        back_populates="chapters",
    )

    # --- Metodos de Negocio ---
    # Preservamos os metodos da versao dataclass.

    def update_content(self, new_content: str, from_ai: bool = False) -> None:
        """Atualiza o conteudo do capitulo.

        Encapsula a logica de atualizacao:
        - Muda o conteudo
        - Registra se veio de IA
        - Atualiza o timestamp

        Args:
            new_content: O novo texto do capitulo
            from_ai: True se o texto foi gerado por IA
        """
        self.content = new_content
        self.ai_generated = from_ai
        self.updated_at = datetime.now(UTC)

    @property
    def word_count(self) -> int:
        """Conta o numero de palavras no conteudo.

        Isso e uma property - chamamos sem parenteses:
            chapter.word_count  (nao chapter.word_count())

        Retorna 0 se o conteudo estiver vazio.
        """
        if not self.content:
            return 0
        return len(self.content.split())

    def __repr__(self) -> str:
        return (
            f"Chapter(id={self.id}, title='{self.title}', "
            f"order={self.order}, words={self.word_count})"
        )
