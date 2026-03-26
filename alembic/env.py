"""
Configuracao do Alembic para migrations do banco de dados.

Este arquivo configura como o Alembic se conecta ao banco e
quais modelos ele deve monitorar para gerar migrations automaticamente.

Conceitos:
- O Alembic usa o metadata do SQLAlchemy para detectar mudancas nos modelos
- A URL do banco vem do .env via pydantic-settings (nao fica hardcoded)
- Importar Base de app.models forca o carregamento de todos os modelos
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# --- Configuracao do projeto ---
# Importar settings para obter a DATABASE_URL do .env
from app.core.config import settings

# IMPORTANTE: Importar Base de app.models (nao de app.core.database)
# Esse import forca o carregamento de User, Project, Chapter,
# registrando todas as tabelas no Base.metadata.
# Sem isso, o Alembic nao conhece nenhuma tabela!
from app.models import Base

# Objeto de configuracao do Alembic (le o alembic.ini)
config = context.config

# Configurar a URL do banco dinamicamente a partir do .env
# Isso substitui a linha "sqlalchemy.url" do alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configurar logging do Python a partir do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos modelos - o Alembic usa isso para detectar mudancas
# e gerar migrations automaticamente (--autogenerate)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Roda migrations em modo 'offline' (sem conexao ao banco).

    Gera o SQL como texto, util para review ou ambientes sem acesso direto ao banco.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda migrations em modo 'online' (com conexao ao banco).

    Cria uma engine, conecta ao banco e executa as migrations.
    Este e o modo padrao usado por `alembic upgrade head`.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
