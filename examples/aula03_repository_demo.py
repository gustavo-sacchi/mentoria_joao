"""
Aula 03 - Repository Pattern: Separando o Acesso ao Banco

Este script demonstra o Repository Pattern na pratica, conectando
ao banco de dados real e executando operacoes CRUD com o UserRepository.

O QUE E O REPOSITORY PATTERN?
==============================
Imagine que voce tem uma aplicacao que precisa salvar e buscar usuarios.
Sem o Repository, o codigo de negocio ficaria cheio de queries SQL:

    # RUIM - SQL misturado com logica de negocio
    def registrar_usuario(email, nome):
        db.execute("INSERT INTO users ...")
        db.execute("SELECT * FROM users WHERE ...")

Com o Repository, isolamos o acesso ao banco em uma camada separada:

    # BOM - logica de negocio usa o repositorio
    def registrar_usuario(email, nome):
        if repo.email_exists(email):
            raise ValueError("Email ja existe")
        user = User(email=email, name=nome, ...)
        repo.create(user)

Vantagens:
- A logica de negocio nao sabe (nem precisa saber) como os dados sao armazenados
- Se trocarmos PostgreSQL por MongoDB, so mudamos o repositorio
- Facil de testar: criamos um repositorio falso (mock) para testes

COMO RODAR:
    uv run python examples/aula03_repository_demo.py

REQUISITOS:
    - Banco de dados configurado (SQLite ou PostgreSQL)
    - Migrations aplicadas: uv run alembic upgrade head
"""

from __future__ import annotations

import sys

# Importamos o que precisamos:
# - session_factory: cria sessoes do banco (a "conversa" com o banco)
# - engine e Base: para garantir que as tabelas existem
# - User: o modelo que vamos manipular
# - UserRepository: o repositorio com metodos especificos de usuario
from app.core.database import Base, engine, session_factory
from app.models.user import User
from app.repositories import UserRepository

# ==================================================
# Secao 0: Preparacao - Garantir que as tabelas existem
# ==================================================
print("=" * 60)
print("PREPARACAO: Criando tabelas no banco (se nao existirem)")
print("=" * 60)

try:
    # Base.metadata.create_all() cria as tabelas que ainda nao existem.
    # Se as tabelas ja existirem (via Alembic), nao faz nada.
    # Isso e util para rodar o script sem precisar de Alembic.
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas com sucesso!")
except Exception as e:
    print(f"\nERRO ao conectar ao banco de dados: {e}")
    print("\nVerifique se:")
    print("  1. O arquivo .env existe com DATABASE_URL configurada")
    print("  2. O banco de dados esta acessivel")
    print("  3. As migrations foram aplicadas: uv run alembic upgrade head")
    sys.exit(1)

# Criamos uma sessao do banco - toda operacao precisa de uma sessao
db = session_factory()

try:
    # Instanciamos o repositorio passando a sessao
    # A partir daqui, usamos repo.metodo() para tudo!
    repo = UserRepository(db)

    # ==================================================
    # Secao 1: Criando um usuario via Repository
    # ==================================================
    print("\n" + "=" * 60)
    print("SECAO 1: Criando um usuario via Repository")
    print("=" * 60)

    # Primeiro verificamos se o email de teste ja existe
    # (para evitar erro de email duplicado ao rodar o script varias vezes)
    email_teste = "joao.teste@email.com"

    if repo.email_exists(email_teste):
        print(f"\nEmail '{email_teste}' ja existe no banco.")
        print("Buscando usuario existente para continuar a demo...")
        user = repo.get_by_email(email_teste)
    else:
        # Criamos a instancia do User (ainda nao esta no banco!)
        user = User(
            email=email_teste,
            name="Joao Teste",
            hashed_password="hash_seguro_aqui",  # Em producao, usar bcrypt!
        )
        print(f"\nUser ANTES de salvar: {user}")
        print(f"  id = {user.id}")  # None - ainda nao tem ID

        # repo.create() faz: db.add() + db.commit() + db.refresh()
        user = repo.create(user)
        print(f"\nUser DEPOIS de salvar: {user}")
        print(f"  id = {user.id}")  # Agora tem um ID do banco!
        print(f"  created_at = {user.created_at}")  # Preenchido pelo banco

    # ==================================================
    # Secao 2: Buscando usuarios
    # ==================================================
    print("\n" + "=" * 60)
    print("SECAO 2: Buscando usuarios")
    print("=" * 60)

    # Busca por ID (metodo herdado do BaseRepository)
    user_by_id = repo.get_by_id(user.id)
    print(f"\nBusca por ID ({user.id}): {user_by_id}")

    # Busca por ID inexistente -> retorna None
    user_fantasma = repo.get_by_id(99999)
    print(f"Busca por ID inexistente (99999): {user_fantasma}")

    # Busca por email (metodo especifico do UserRepository)
    user_by_email = repo.get_by_email(email_teste)
    print(f"\nBusca por email ('{email_teste}'): {user_by_email}")

    # Busca por email inexistente -> retorna None
    user_inexistente = repo.get_by_email("nao.existe@email.com")
    print(f"Busca por email inexistente: {user_inexistente}")

    # Listar todos (metodo herdado do BaseRepository)
    todos = repo.get_all()
    print(f"\nTodos os usuarios ({len(todos)} encontrados):")
    for u in todos:
        print(f"  - {u}")

    # ==================================================
    # Secao 3: Atualizando um usuario
    # ==================================================
    print("\n" + "=" * 60)
    print("SECAO 3: Atualizando um usuario")
    print("=" * 60)

    nome_antigo = user.name
    user.name = "Joao Atualizado"

    # repo.update() faz: db.commit() + db.refresh()
    # O SQLAlchemy detecta a mudanca automaticamente (dirty tracking)
    user = repo.update(user)
    print(f"\nNome alterado: '{nome_antigo}' -> '{user.name}'")

    # Verificando que a mudanca persistiu no banco
    user_verificado = repo.get_by_id(user.id)
    print(f"Verificacao (buscou novamente): {user_verificado}")
    print(f"  name = '{user_verificado.name}'")  # type: ignore[union-attr]

    # Restaurar o nome original
    user.name = "Joao Teste"
    user = repo.update(user)

    # ==================================================
    # Secao 4: Verificando existencia de email
    # ==================================================
    print("\n" + "=" * 60)
    print("SECAO 4: Verificando existencia de email")
    print("=" * 60)

    # email_exists() e util antes de criar um novo usuario
    existe = repo.email_exists(email_teste)
    print(f"\nEmail '{email_teste}' existe? {existe}")  # True

    nao_existe = repo.email_exists("ninguem@email.com")
    print(f"Email 'ninguem@email.com' existe? {nao_existe}")  # False

    # Simulando validacao de registro
    email_novo = "novo.usuario@email.com"
    if repo.email_exists(email_novo):
        print(f"\nERRO: Nao pode registrar, email '{email_novo}' ja existe!")
    else:
        print(f"\nOK: Email '{email_novo}' disponivel para registro!")

    # ==================================================
    # Secao 5: Contando registros
    # ==================================================
    print("\n" + "=" * 60)
    print("SECAO 5: Contando registros")
    print("=" * 60)

    total = repo.count()
    print(f"\nTotal de usuarios no banco: {total}")

    # Exemplo de uso com paginacao
    # Se tivessemos 100 usuarios e quisessemos 10 por pagina:
    # pagina 1: repo.get_all(skip=0, limit=10)
    # pagina 2: repo.get_all(skip=10, limit=10)
    # pagina 3: repo.get_all(skip=20, limit=10)
    print(f"Com paginacao de 10 por pagina, teriamos {(total + 9) // 10} pagina(s)")

    # ==================================================
    # Secao 6: Limpeza - Deletando o usuario de teste
    # ==================================================
    print("\n" + "=" * 60)
    print("SECAO 6: Limpeza - Deletando o usuario de teste")
    print("=" * 60)

    print(f"\nDeletando usuario: {user}")
    repo.delete(user)

    # Verificando que foi deletado
    user_deletado = repo.get_by_email(email_teste)
    print(f"Busca apos deletar: {user_deletado}")  # None

    total_apos = repo.count()
    print(f"Total de usuarios apos limpeza: {total_apos}")

    # ==================================================
    # Resumo da Aula
    # ==================================================
    print("\n" + "=" * 60)
    print("RESUMO DA AULA 03")
    print("=" * 60)
    print("""
O Repository Pattern separa o COMO acessar dados do QUE fazer com eles:

    BaseRepository (generico):
    - get_by_id()   -> busca por ID
    - get_all()     -> lista com paginacao
    - create()      -> insere no banco
    - update()      -> atualiza no banco
    - delete()      -> remove do banco
    - count()       -> conta registros

    UserRepository (especializado):
    - get_by_email()     -> busca por email
    - get_active_users() -> lista apenas ativos
    - deactivate()       -> desativa (soft delete)
    - email_exists()     -> verifica duplicidade

Proxima aula: ProjectRepository e ChapterRepository com queries
mais avancadas, filtros combinados e relacionamentos!
""")

finally:
    # IMPORTANTE: Sempre fechar a sessao ao terminar!
    # O try/finally garante que a sessao sera fechada mesmo se
    # ocorrer um erro durante a execucao do script.
    db.close()
    print("Sessao do banco fechada. Ate a proxima aula!")
