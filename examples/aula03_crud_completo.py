"""
Aula 03 - CRUD Completo: Projetos e Capitulos

Este script demonstra o fluxo CRUD end-to-end usando TODOS os repositorios:
UserRepository, ProjectRepository e ChapterRepository.

Vamos criar um usuario, um projeto com capitulos, buscar, filtrar,
atualizar e por fim limpar tudo. Cada passo ensina um conceito diferente.

FLUXO DO SCRIPT (10 passos):
============================
1. Criar usuario                    -> UserRepository.create
2. Criar projeto                    -> ProjectRepository.create
3. Adicionar capitulos              -> ChapterRepository.create (3 capitulos)
4. Buscar projeto com capitulos     -> ProjectRepository.get_with_chapters (eager)
5. Buscar capitulos ordenados       -> ChapterRepository.get_by_project
6. Pesquisar projetos por titulo    -> ProjectRepository.search_by_title
7. Proximo numero de ordem          -> ChapterRepository.get_next_order
8. Atualizar capitulo com IA        -> Chapter.update_content + ChapterRepository.update
9. Filtrar capitulos de IA          -> ChapterRepository.get_ai_generated
10. Limpeza                         -> Deletar tudo na ordem correta

COMO RODAR:
    uv run python examples/aula03_crud_completo.py

REQUISITOS:
    - Banco de dados configurado (SQLite ou PostgreSQL)
    - Migrations aplicadas: uv run alembic upgrade head
"""

from __future__ import annotations

import sys

from app.core.database import Base, engine, session_factory
from app.models.chapter import Chapter
from app.models.project import Project
from app.models.user import User
from app.repositories import ChapterRepository, ProjectRepository, UserRepository

# ==================================================
# Preparacao: Garantir que as tabelas existem
# ==================================================
print("=" * 60)
print("PREPARACAO: Criando tabelas no banco (se nao existirem)")
print("=" * 60)

try:
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
    # Instanciamos os 3 repositorios, todos usando a MESMA sessao.
    # Isso e importante: operacoes na mesma sessao compartilham
    # a mesma transacao, garantindo consistencia dos dados.
    user_repo = UserRepository(db)
    project_repo = ProjectRepository(db)
    chapter_repo = ChapterRepository(db)

    # ==================================================
    # Passo 1: Criando um usuario
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 1: Criando um usuario")
    print("=" * 60)

    email_teste = "autor.teste@email.com"

    # Limpar dados de execucoes anteriores (se existir)
    existing_user = user_repo.get_by_email(email_teste)
    if existing_user:
        print(f"Limpando dados de execucao anterior...")
        # Deletar o usuario tambem deleta seus projetos e capitulos
        # gracias ao cascade="all, delete-orphan" nos relacionamentos
        user_repo.delete(existing_user)

    user = User(
        email=email_teste,
        name="Autor Teste",
        hashed_password="hash_seguro_aqui",
    )
    user = user_repo.create(user)
    print(f"Usuario criado: {user}")
    print(f"  ID: {user.id}")

    # ==================================================
    # Passo 2: Criando um projeto
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 2: Criando um projeto")
    print("=" * 60)

    project = Project(
        user_id=user.id,
        title="Aprenda Python do Zero",
        description="Um guia pratico para iniciantes em Python.",
    )
    project = project_repo.create(project)
    print(f"Projeto criado: {project}")
    print(f"  ID: {project.id}")
    print(f"  Status: {project.status}")  # "draft" (padrao)

    # Criar um segundo projeto para demonstrar buscas
    project2 = Project(
        user_id=user.id,
        title="Python Avancado: Patterns e Boas Praticas",
        description="Para quem ja sabe o basico.",
    )
    project2 = project_repo.create(project2)
    print(f"Projeto 2 criado: {project2}")

    # ==================================================
    # Passo 3: Adicionando capitulos
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 3: Adicionando capitulos ao projeto")
    print("=" * 60)

    # Criamos 3 capitulos com ordens diferentes
    chapters_data = [
        {"title": "Introducao ao Python", "order": 1, "content": "Python e uma linguagem de programacao versatil e poderosa."},
        {"title": "Variaveis e Tipos", "order": 2, "content": "Em Python, variaveis sao criadas na atribuicao."},
        {"title": "Estruturas de Controle", "order": 3, "content": ""},
    ]

    created_chapters = []
    for data in chapters_data:
        chapter = Chapter(
            project_id=project.id,
            title=data["title"],
            order=data["order"],
            content=data["content"],
        )
        chapter = chapter_repo.create(chapter)
        created_chapters.append(chapter)
        print(f"  Capitulo criado: {chapter}")

    print(f"\nTotal de capitulos criados: {len(created_chapters)}")

    # ==================================================
    # Passo 4: Buscando projeto com capitulos (Eager Loading)
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 4: Buscando projeto com capitulos (Eager Loading)")
    print("=" * 60)

    # CONCEITO: joinedload carrega os capitulos junto com o projeto
    # em uma UNICA query SQL (com JOIN), em vez de fazer queries extras
    project_with_chapters = project_repo.get_with_chapters(project.id)

    if project_with_chapters:
        print(f"Projeto: {project_with_chapters.title}")
        print(f"Capitulos carregados (eager loading - sem query extra!):")
        for ch in project_with_chapters.chapters:
            print(f"  Cap {ch.order}: {ch.title} ({ch.word_count} palavras)")
    else:
        print("Projeto nao encontrado!")

    # ==================================================
    # Passo 5: Buscando capitulos ordenados
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 5: Buscando capitulos ordenados por posicao")
    print("=" * 60)

    # get_by_project ordena automaticamente pela coluna 'order'
    chapters_ordered = chapter_repo.get_by_project(project.id)
    print(f"Capitulos do projeto (ordenados por 'order' ASC):")
    for ch in chapters_ordered:
        print(f"  {ch.order}. {ch.title}")

    # get_by_project_ordered e um alias didatico (faz a mesma coisa)
    chapters_alias = chapter_repo.get_by_project_ordered(project.id)
    print(f"\nUsando get_by_project_ordered (alias): {len(chapters_alias)} capitulos")

    # ==================================================
    # Passo 6: Pesquisando projetos por titulo
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 6: Pesquisando projetos por titulo (ilike)")
    print("=" * 60)

    # search_by_title usa ilike: busca case-insensitive
    # "python" encontra "Python", "PYTHON", "python", etc.
    results = project_repo.search_by_title(user_id=user.id, search="python")
    print(f"Busca por 'python': {len(results)} projeto(s) encontrado(s)")
    for p in results:
        print(f"  - {p.title}")

    # Busca mais especifica
    results2 = project_repo.search_by_title(user_id=user.id, search="avancado")
    print(f"\nBusca por 'avancado': {len(results2)} projeto(s) encontrado(s)")
    for p in results2:
        print(f"  - {p.title}")

    # Busca sem resultados
    results3 = project_repo.search_by_title(user_id=user.id, search="javascript")
    print(f"\nBusca por 'javascript': {len(results3)} projeto(s) encontrado(s)")

    # ==================================================
    # Passo 7: Proximo numero de ordem
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 7: Calculando proxima posicao com get_next_order")
    print("=" * 60)

    # get_next_order usa func.max() + func.coalesce() em uma unica query SQL
    next_order = chapter_repo.get_next_order(project.id)
    print(f"Proxima posicao disponivel no projeto: {next_order}")
    print(f"  (temos capitulos 1, 2, 3 -> proxima e 4)")

    # Para um projeto sem capitulos, retornaria 1
    next_order_empty = chapter_repo.get_next_order(project2.id)
    print(f"Proxima posicao no projeto 2 (sem capitulos): {next_order_empty}")

    # ==================================================
    # Passo 8: Atualizando capitulo com conteudo de IA
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 8: Atualizando capitulo com conteudo de IA")
    print("=" * 60)

    # Pegamos o capitulo 3 (que estava vazio) e adicionamos conteudo "de IA"
    chapter3 = created_chapters[2]  # "Estruturas de Controle"
    print(f"ANTES: {chapter3}")
    print(f"  content: '{chapter3.content}'")
    print(f"  ai_generated: {chapter3.ai_generated}")
    print(f"  word_count: {chapter3.word_count}")

    # Usamos o metodo de negocio update_content() do modelo
    # Ele marca ai_generated=True e atualiza o timestamp
    chapter3.update_content(
        new_content="O if/elif/else permite executar blocos de codigo "
                    "condicionalmente. O for e while servem para repeticao. "
                    "Estas sao as estruturas de controle fundamentais do Python.",
        from_ai=True,
    )

    # Salvamos no banco via repositorio
    chapter3 = chapter_repo.update(chapter3)
    print(f"\nDEPOIS: {chapter3}")
    print(f"  ai_generated: {chapter3.ai_generated}")  # True
    print(f"  word_count: {chapter3.word_count}")

    # ==================================================
    # Passo 9: Filtrando capitulos gerados por IA
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 9: Filtrando capitulos gerados por IA")
    print("=" * 60)

    ai_chapters = chapter_repo.get_ai_generated(project.id)
    print(f"Capitulos gerados por IA: {len(ai_chapters)}")
    for ch in ai_chapters:
        print(f"  - {ch.title} ({ch.word_count} palavras)")

    # Mostrar tambem os NaO gerados por IA para comparacao
    all_chapters = chapter_repo.get_by_project(project.id)
    manual_chapters = [ch for ch in all_chapters if not ch.ai_generated]
    print(f"\nCapitulos escritos manualmente: {len(manual_chapters)}")
    for ch in manual_chapters:
        print(f"  - {ch.title} ({ch.word_count} palavras)")

    # Estatisticas do usuario
    total_projects = project_repo.count_by_user(user.id)
    total_chapters = chapter_repo.count()
    print(f"\nEstatisticas do usuario:")
    print(f"  Projetos: {total_projects}")
    print(f"  Capitulos: {total_chapters}")

    # ==================================================
    # Passo 10: Limpeza
    # ==================================================
    print("\n" + "=" * 60)
    print("PASSO 10: Limpeza - Deletando dados de teste")
    print("=" * 60)

    # IMPORTANTE: a ordem de delecao importa por causa das ForeignKeys!
    # Opção 1: deletar na ordem inversa (capitulos -> projeto -> usuario)
    # Opção 2: deletar o usuario (cascade deleta tudo automaticamente)
    #
    # Vamos usar a opcao 2 para demonstrar o CASCADE:
    print(f"Deletando usuario '{user.name}' (cascade deleta projetos e capitulos)...")
    user_repo.delete(user)

    # Verificando que tudo foi deletado
    user_check = user_repo.get_by_email(email_teste)
    project_check = project_repo.get_by_id(project.id)
    chapters_check = chapter_repo.get_by_project(project.id)

    print(f"  Usuario: {user_check}")    # None
    print(f"  Projeto: {project_check}")  # None
    print(f"  Capitulos: {chapters_check}")  # []

    print("\nLimpeza concluida com sucesso!")

    # ==================================================
    # Resumo da Aula
    # ==================================================
    print("\n" + "=" * 60)
    print("RESUMO DA AULA 03 - CRUD COMPLETO")
    print("=" * 60)
    print("""
Nesta aula aprendemos a usar 3 repositorios juntos:

  UserRepository     -> CRUD de usuarios
  ProjectRepository  -> CRUD de projetos + queries avancadas
  ChapterRepository  -> CRUD de capitulos + ordenacao

Conceitos novos:
  1. EAGER LOADING (joinedload):
     Carrega relacionamentos em 1 query (em vez de N+1)

  2. ILIKE (busca case-insensitive):
     Encontra "Python", "PYTHON", "python" com uma unica busca

  3. func.max() e func.coalesce():
     Funcoes SQL para calcular a proxima posicao de um capitulo

  4. FILTROS COMPOSTOS:
     Combinar user_id + status, project_id + ai_generated, etc.

  5. CASCADE DELETE:
     Deletar o usuario automaticamente deleta projetos e capitulos

Proxima aula: Autenticacao! Vamos criar o AuthService com JWT,
hashing de senhas com bcrypt, e proteger nossos endpoints.
""")

finally:
    # IMPORTANTE: Sempre fechar a sessao ao terminar!
    db.close()
    print("Sessao do banco fechada. Ate a proxima aula!")
