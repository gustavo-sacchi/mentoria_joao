"""
Aula 02 - De Dataclass para SQLAlchemy Model (OOP -> ORM)

Este script demonstra como as classes Python que criamos na Aula 01
foram transformadas em modelos SQLAlchemy que sabem se comunicar
com um banco de dados.

IMPORTANTE: Este script NAO conecta ao banco de dados!
Apenas inspeciona a estrutura dos modelos para entender o mapeamento.

Para rodar: uv run python examples/aula02_sqlalchemy_models.py
"""

from __future__ import annotations

from app.models import Base, Chapter, Project, ProjectStatus, User

# ==================================================
# Secao 1: De dataclass para SQLAlchemy Model
# ==================================================
print("=" * 60)
print("SECAO 1: De dataclass para SQLAlchemy Model")
print("=" * 60)

# Na Aula 01, nossas classes usavam @dataclass:
#
#   @dataclass(slots=True)
#   class User:
#       id: int | None
#       email: str
#       ...
#
# Agora, nossas classes herdam de Base (SQLAlchemy):
#
#   class User(Base):
#       __tablename__ = "users"
#       id: Mapped[int] = mapped_column(primary_key=True)
#       email: Mapped[str] = mapped_column(String(255), unique=True)
#       ...
#
# A principal diferenca: o SQLAlchemy sabe COMO transformar cada
# atributo Python em uma coluna de banco de dados!

# Podemos criar um User sem banco de dados (igual a antes)
user = User(
    email="joao@email.com",
    name="Joao",
    hashed_password="hash_seguro_aqui",
)

print(f"User criado (sem banco): {user}")
print(f"  email: {user.email}")
print(f"  name: {user.name}")
print(f"  is_active: {user.is_active}")  # None! (ver nota abaixo)
print(f"  id: {user.id}")  # None - ainda nao foi salvo no banco

# NOTA IMPORTANTE sobre defaults:
# is_active aparece como None porque o 'default=' no mapped_column
# e um INSERT default - so e aplicado quando o banco salva o registro.
# Se quiser o valor agora, passe explicitamente: User(is_active=True, ...)
# O mesmo vale para 'created_at' (server_default - gerado pelo banco).
# Isso e diferente do @dataclass, onde defaults funcionam no __init__.

# Demonstrando com valor explicito:
user_explicito = User(
    email="maria@email.com",
    name="Maria",
    hashed_password="hash_seguro",
    is_active=True,
)
print(f"\nUser com is_active explicito: is_active={user_explicito.is_active}")

print()

# ==================================================
# Secao 2: Inspecionando o modelo
# ==================================================
print("=" * 60)
print("SECAO 2: Inspecionando o modelo (introspeccao)")
print("=" * 60)

# O SQLAlchemy guarda muitas informacoes sobre cada modelo.
# Podemos inspecionar essas informacoes sem precisar do banco!

# __tablename__: nome da tabela no banco
print(f"Tabela do User: {User.__tablename__}")
print(f"Tabela do Project: {Project.__tablename__}")
print(f"Tabela do Chapter: {Chapter.__tablename__}")

print()

# __table__.columns: lista todas as colunas da tabela
print("Colunas da tabela 'users':")
for coluna in User.__table__.columns:
    # Cada coluna tem: nome, tipo, se e nullable, se e primary_key, etc.
    nullable = "NULL" if coluna.nullable else "NOT NULL"
    pk = " (PK)" if coluna.primary_key else ""
    unique = " (UNIQUE)" if coluna.unique else ""
    print(f"  {coluna.name}: {coluna.type} {nullable}{pk}{unique}")

print()

# Vamos ver as colunas de Project tambem
print("Colunas da tabela 'projects':")
for coluna in Project.__table__.columns:
    nullable = "NULL" if coluna.nullable else "NOT NULL"
    pk = " (PK)" if coluna.primary_key else ""
    fk_info = ""
    if coluna.foreign_keys:
        # foreign_keys e um set de ForeignKey objects
        fk_target = list(coluna.foreign_keys)[0].target_fullname
        fk_info = f" (FK -> {fk_target})"
    print(f"  {coluna.name}: {coluna.type} {nullable}{pk}{fk_info}")

print()

# ==================================================
# Secao 3: Relacionamentos
# ==================================================
print("=" * 60)
print("SECAO 3: Relacionamentos entre modelos")
print("=" * 60)

# relationship() cria atributos que conectam modelos entre si.
# Nao cria coluna no banco - apenas facilita o acesso em Python!
#
# A ForeignKey cria a conexao NO BANCO: user_id -> users.id
# O relationship cria a conexao NO PYTHON: user.projects / project.owner

# Inspecionando relacionamentos do User
print("Relacionamentos do User:")
for nome, rel in User.__mapper__.relationships.items():
    direcao = "1:N" if rel.uselist else "N:1"
    cascade = rel.cascade
    print(f"  {nome}: {direcao} -> {rel.mapper.class_.__name__}")
    print(f"    cascade: {cascade}")

print()

# Inspecionando relacionamentos do Project
print("Relacionamentos do Project:")
for nome, rel in Project.__mapper__.relationships.items():
    direcao = "1:N" if rel.uselist else "N:1"
    print(f"  {nome}: {direcao} -> {rel.mapper.class_.__name__}")

print()

# Inspecionando relacionamentos do Chapter
print("Relacionamentos do Chapter:")
for nome, rel in Chapter.__mapper__.relationships.items():
    direcao = "1:N" if rel.uselist else "N:1"
    print(f"  {nome}: {direcao} -> {rel.mapper.class_.__name__}")

print()

# Explicacao visual dos relacionamentos:
print("Diagrama de relacionamentos:")
print("  User (1) ----< (N) Project (1) ----< (N) Chapter")
print("        |                    |")
print("  User.projects        Project.chapters")
print("  Project.owner        Chapter.project")
print()
print("  Leitura: Um User tem varios Projects.")
print("           Um Project tem varios Chapters.")
print("           Cada Project pertence a um User (owner).")
print("           Cada Chapter pertence a um Project.")

print()

# ==================================================
# Secao 4: Metadata e tabelas
# ==================================================
print("=" * 60)
print("SECAO 4: Metadata - registro de todas as tabelas")
print("=" * 60)

# Base.metadata e o "catalogo" de todas as tabelas do sistema.
# Quando importamos todos os modelos, eles se registram automaticamente.
# O Alembic usa esse metadata para gerar migrations!

print(f"Total de tabelas registradas: {len(Base.metadata.tables)}")
print()

for nome_tabela, tabela in Base.metadata.tables.items():
    num_colunas = len(tabela.columns)
    num_fks = sum(1 for c in tabela.columns if c.foreign_keys)
    print(f"Tabela: {nome_tabela}")
    print(f"  Colunas: {num_colunas}")
    print(f"  Foreign Keys: {num_fks}")
    print(f"  Nomes das colunas: {[c.name for c in tabela.columns]}")
    print()

# O Enum ProjectStatus continua funcionando igual
print("Bonus - Enum ProjectStatus (nao mudou!):")
for status in ProjectStatus:
    print(f"  {status.name} = '{status.value}'")

print()

# ==================================================
# Secao 5: Metodos de negocio preservados
# ==================================================
print("=" * 60)
print("SECAO 5: Metodos de negocio (preservados do dataclass)")
print("=" * 60)

# Os metodos que criamos na Aula 01 continuam funcionando!
# Modelos SQLAlchemy sao classes Python normais - podem ter metodos.

# Passamos status explicitamente (lembre: default= so funciona no INSERT do banco)
projeto = Project(
    title="Meu Ebook",
    description="Sobre Python",
    status=ProjectStatus.DRAFT.value,
)
print(f"Projeto: {projeto}")
print(f"Status inicial: {projeto.status}")

projeto.mark_in_progress()
print(f"Apos mark_in_progress(): {projeto.status}")
print(f"Updated_at: {projeto.updated_at}")

projeto.mark_completed()
print(f"Apos mark_completed(): {projeto.status}")

print()

# Property word_count tambem funciona
capitulo = Chapter(
    title="Introducao",
    content="Python e uma linguagem de programacao poderosa e acessivel",
)
print(f"Capitulo: {capitulo.title}")
print(f"Conteudo: '{capitulo.content}'")
print(f"Palavras: {capitulo.word_count}")  # Property - sem parenteses!

capitulo.update_content(
    "Python foi criado por Guido van Rossum. E muito usado em data science.",
    from_ai=True,
)
print(f"\nApos update_content (IA):")
print(f"Conteudo: '{capitulo.content}'")
print(f"Palavras: {capitulo.word_count}")
print(f"Gerado por IA: {capitulo.ai_generated}")

print()
print("=" * 60)
print("FIM DA DEMONSTRACAO - Aula 02")
print("=" * 60)
print()
print("Proximos passos (Aula 02 continuacao):")
print("  - Configurar PostgreSQL com Docker")
print("  - Usar Alembic para criar as tabelas no banco")
print("  - Testar insert/select de dados reais")
