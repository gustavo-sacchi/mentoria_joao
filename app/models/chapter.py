"""
Modelo de dominio: Chapter (Capitulo de Ebook)

Classe Python pura que representa um capitulo de ebook.
Demonstra metodos que recebem parametros e properties calculadas.

Conceitos ensinados:
- Metodos com parametros e valores padrao
- Property calculada (word_count)
- Flag booleana para rastrear origem do conteudo (IA vs humano)
- Composicao (Chapter pertence a um Project via project_id)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class Chapter:
    """Representa um capitulo dentro de um projeto de ebook.

    Cada capitulo tem um conteudo de texto, uma ordem no ebook,
    e uma flag que indica se o texto foi gerado por IA.

    Atributos:
        id: Identificador unico (None quando nao salvo)
        project_id: ID do projeto ao qual este capitulo pertence
        title: Titulo do capitulo
        content: Texto do capitulo (pode estar vazio inicialmente)
        order: Posicao do capitulo no ebook (0 = primeiro)
        ai_generated: Se o conteudo foi gerado por IA
        created_at: Data/hora de criacao
        updated_at: Data/hora da ultima atualizacao
    """

    id: int | None
    project_id: int
    title: str
    created_at: datetime
    content: str = ""
    order: int = 0
    ai_generated: bool = False
    updated_at: datetime | None = None

    def update_content(self, new_content: str, from_ai: bool = False) -> None:
        """Atualiza o conteudo do capitulo.

        Este metodo encapsula a logica de atualizacao:
        - Muda o conteudo
        - Registra se veio de IA
        - Atualiza o timestamp

        Args:
            new_content: O novo texto do capitulo
            from_ai: True se o texto foi gerado por IA, False se escrito pelo usuario
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
