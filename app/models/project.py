"""
Modelo de dominio: Project (Projeto de Ebook)

Classe Python pura que representa um projeto de ebook.
Demonstra o uso de Enum para controlar estados validos.

Conceitos ensinados:
- Enum (conjunto fixo de valores possiveis)
- Metodos que alteram estado do objeto
- Atributos opcionais com valor padrao
- Composicao (Project pertence a um User via user_id)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum


class ProjectStatus(Enum):
    """Status possiveis de um projeto de ebook.

    Usar Enum garante que o status so pode ser um destes valores.
    Tentar usar um valor invalido gera erro - muito melhor que string livre!

    Exemplo:
        status = ProjectStatus.DRAFT       # OK
        status = ProjectStatus("draft")    # OK (pelo valor)
        status = "qualquer_coisa"          # Nao e um ProjectStatus!
    """

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass(slots=True)
class Project:
    """Representa um projeto de ebook no sistema.

    Um projeto pertence a um usuario (user_id) e contem capitulos.
    O fluxo normal e: DRAFT -> IN_PROGRESS -> COMPLETED

    Atributos:
        id: Identificador unico (None quando nao salvo)
        user_id: ID do usuario dono do projeto
        title: Titulo do ebook
        description: Descricao opcional do projeto
        status: Estado atual (draft, in_progress, completed)
        created_at: Data/hora de criacao
        updated_at: Data/hora da ultima atualizacao (None se nunca atualizado)
    """

    id: int | None
    user_id: int
    title: str
    created_at: datetime
    description: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    updated_at: datetime | None = None

    def mark_in_progress(self) -> None:
        """Marca o projeto como 'em andamento'.

        Este metodo encapsula a logica de mudanca de estado.
        Em vez de fazer project.status = ... diretamente,
        usamos um metodo que tambem atualiza o updated_at.
        """
        self.status = ProjectStatus.IN_PROGRESS
        self.updated_at = datetime.now(UTC)

    def mark_completed(self) -> None:
        """Marca o projeto como concluido.

        Atualiza o status e registra quando foi finalizado.
        """
        self.status = ProjectStatus.COMPLETED
        self.updated_at = datetime.now(UTC)
