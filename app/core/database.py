"""
Configuracao do banco de dados com SQLAlchemy 2.0.

Este modulo configura a conexao com o PostgreSQL usando SQLAlchemy.
Todos os modelos herdam da classe Base definida aqui.

Conceitos ensinados:
- Engine: a "ponte" entre Python e o banco de dados
- Session: uma "conversa" com o banco (abre, faz operacoes, fecha)
- DeclarativeBase: classe mae de todos os modelos (SQLAlchemy 2.0)
- Generator (yield): funcao que "empresta" algo e depois limpa

Importante:
- Usamos SQLAlchemy 2.0 SINCRONO (nao async)
- O estilo 2.0 usa DeclarativeBase, Mapped e mapped_column
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# --- Engine ---
# O engine e a conexao "bruta" com o banco de dados.
# Ele gerencia um pool de conexoes para reutilizacao.
# echo=False desativa logs de SQL (mude para True para debugar queries).
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
)


# --- SessionLocal ---
# SessionLocal e uma "fabrica" de sessoes.
# Cada vez que chamamos SessionLocal(), criamos uma nova sessao.
# - autocommit=False: nos controlamos quando salvar (commit)
# - autoflush=False: nos controlamos quando sincronizar com o banco
session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# --- Base Declarativa ---
# Todos os modelos SQLAlchemy herdam desta classe.
# Ela contem o "metadata" - registro de todas as tabelas do sistema.
# SQLAlchemy 2.0 usa DeclarativeBase em vez do antigo declarative_base().
class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy.

    Ao herdar de Base, uma classe Python automaticamente vira uma tabela.
    A Base tambem armazena o metadata com informacoes de todas as tabelas.

    Exemplo:
        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    pass


# --- Dependency Injection ---
# Esta funcao sera usada pelo FastAPI para injetar sessoes nos endpoints.
# O pattern "yield" garante que a sessao SEMPRE sera fechada,
# mesmo se ocorrer um erro durante o processamento.
def get_db() -> Generator[Session, None, None]:
    """Cria uma sessao do banco e garante que sera fechada ao final.

    Uso com FastAPI (veremos nas proximas aulas):
        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            ...

    O 'yield' funciona assim:
    1. Cria a sessao (db = session_factory())
    2. "Empresta" para quem pediu (yield db)
    3. Quando terminar, fecha a sessao (finally: db.close())
    """
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
