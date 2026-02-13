"""
Modelo SQLAlchemy: User (Usuario)

ANTES (Aula 01): Usavamos @dataclass para definir a estrutura do User.
AGORA (Aula 02): Usamos SQLAlchemy para mapear a classe para uma tabela no banco.

A classe continua sendo Python puro, mas agora o SQLAlchemy sabe como
transformar cada atributo em uma coluna do banco de dados.

Conceitos ensinados:
- Base: classe mae que conecta o modelo ao banco
- __tablename__: nome da tabela no banco de dados
- Mapped[tipo]: declara o tipo da coluna (SQLAlchemy 2.0)
- mapped_column(): configura a coluna (primary_key, unique, etc.)
- relationship(): define relacao entre tabelas (User -> Projects)
- server_default: valor padrao gerado pelo BANCO (nao pelo Python)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# TYPE_CHECKING: este bloco so roda durante checagem de tipos (mypy/pyright),
# NAO roda em tempo de execucao. Isso evita importacoes circulares!
if TYPE_CHECKING:
    from app.models.project import Project


class User(Base):
    """Modelo de usuario mapeado para a tabela 'users' no banco.

    Comparacao com a versao dataclass:
    - ANTES: @dataclass definia a estrutura, mas nao sabia nada do banco
    - AGORA: User(Base) herda de Base, e o SQLAlchemy cria a tabela automaticamente

    Cada atributo 'Mapped[tipo]' vira uma coluna no banco:
    - Mapped[int] -> INTEGER
    - Mapped[str] -> VARCHAR
    - Mapped[bool] -> BOOLEAN
    - Mapped[datetime] -> TIMESTAMP

    Relacionamentos:
    - Um User pode ter varios Projects (relacao 1:N)
    """

    __tablename__ = "users"

    # --- Colunas ---
    # primary_key=True: esta coluna e o identificador unico (auto-incrementa)
    id: Mapped[int] = mapped_column(primary_key=True)

    # unique=True: nao pode ter dois usuarios com o mesmo email
    # index=True: cria um indice para buscas rapidas por email
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(100))

    # A senha NUNCA e armazenada em texto puro - sempre o hash
    hashed_password: Mapped[str] = mapped_column(String(255))

    # default=True: o Python define o valor padrao ao criar o objeto
    is_active: Mapped[bool] = mapped_column(default=True)

    # server_default=func.now(): o BANCO define a data/hora ao inserir o registro.
    # Isso e melhor que usar Python pois garante consistencia com o fuso horario do banco.
    # DateTime(timezone=True) = TIMESTAMP WITH TIME ZONE no PostgreSQL
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # --- Relacionamentos ---
    # relationship() nao cria coluna no banco - cria um atributo Python
    # que permite acessar os projetos de um usuario diretamente.
    #
    # "Project" (string): referencia ao modelo Project resolvida pelo SQLAlchemy.
    #   Usar string evita importacao circular (User importa Project que importa User).
    #
    # back_populates="owner": cria vinculo bidirecional com Project.owner
    # cascade="all, delete-orphan": se deletar o usuario, deleta seus projetos
    #
    # Exemplo de uso (veremos nas proximas aulas):
    #   user.projects  -> retorna lista de Project deste usuario
    projects: Mapped[list[Project]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Representacao do objeto para debug.

        IMPORTANTE: Nunca mostramos a senha no __repr__!
        Isso evita que a senha apareca em logs ou prints acidentais.
        """
        return f"User(id={self.id}, email='{self.email}', name='{self.name}')"
