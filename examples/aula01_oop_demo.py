"""
Aula 01 - Demonstracao de Programacao Orientada a Objetos (OOP)

Este script demonstra os conceitos fundamentais de OOP usando as classes
de dominio do projeto Ebook Creator.

Para rodar: uv run python examples/aula01_oop_demo.py
"""

from __future__ import annotations

from datetime import UTC, datetime

from examples.aula01_models_puro import Chapter, Project, ProjectStatus, User

# ==================================================
# Secao 1: Criando objetos (instancias)
# ==================================================
print("=" * 50)
print("SECAO 1: Criando objetos (instancias)")
print("=" * 50)

# Uma classe e como uma "planta" (blueprint) - ela define a estrutura.
# Um objeto (instancia) e uma "casa" construida a partir dessa planta.
# Podemos criar quantas casas quisermos a partir da mesma planta!

# Criando um usuario - cada parametro e um "atributo" do objeto
usuario = User(
    id=1,
    email="joao@email.com",
    name="Joao",
    hashed_password="senha_criptografada_aqui",
    created_at=datetime.now(UTC),
)

# O __repr__ customizado mostra informacoes uteis (sem a senha!)
print(f"Usuario criado: {usuario}")
print(f"Nome: {usuario.name}")
print(f"Email: {usuario.email}")
print(f"Ativo: {usuario.is_active}")

# Criando outro usuario - mesma classe, dados diferentes
admin = User(
    id=2,
    email="admin@email.com",
    name="Admin",
    hashed_password="outra_senha_hash",
    created_at=datetime.now(UTC),
    is_active=True,
)

print(f"Admin criado: {admin}")
print()

# Demonstrando validacao do __post_init__
print("Tentando criar usuario com email vazio...")
try:
    usuario_invalido = User(
        id=None,
        email="",  # Vai dar erro!
        name="Teste",
        hashed_password="xxx",
        created_at=datetime.now(UTC),
    )
except ValueError as erro:
    print(f"Erro capturado: {erro}")

print()

# ==================================================
# Secao 2: Usando metodos
# ==================================================
print("=" * 50)
print("SECAO 2: Usando metodos")
print("=" * 50)

# Metodos sao funcoes que pertencem a um objeto.
# Eles podem ler e modificar os atributos do objeto.

# Criando um projeto de ebook
projeto = Project(
    id=1,
    user_id=usuario.id,  # Referencia ao usuario dono
    title="Meu Primeiro Ebook",
    description="Um ebook sobre Python para iniciantes",
    created_at=datetime.now(UTC),
)

print(f"Projeto: {projeto.title}")
print(f"Status inicial: {projeto.status}")
print(f"Atualizado em: {projeto.updated_at}")

# Usando o metodo mark_in_progress()
# O metodo encapsula a logica: muda status E atualiza timestamp
projeto.mark_in_progress()
print(f"\nApos mark_in_progress():")
print(f"Status: {projeto.status}")
print(f"Atualizado em: {projeto.updated_at}")

# Usando o metodo mark_completed()
projeto.mark_completed()
print(f"\nApos mark_completed():")
print(f"Status: {projeto.status}")
print(f"Atualizado em: {projeto.updated_at}")

# Criando um capitulo e usando update_content()
capitulo = Chapter(
    id=1,
    project_id=projeto.id,
    title="Introducao",
    created_at=datetime.now(UTC),
)

print(f"\nCapitulo: {capitulo.title}")
print(f"Conteudo inicial: '{capitulo.content}'")

# Atualizando conteudo - escrito pelo usuario
capitulo.update_content("Python e uma linguagem incrivel para iniciantes.")
print(f"Conteudo atualizado: '{capitulo.content}'")
print(f"Gerado por IA: {capitulo.ai_generated}")

# Atualizando conteudo - gerado por IA
capitulo.update_content(
    "Python e uma linguagem de programacao versatil e poderosa.",
    from_ai=True,
)
print(f"Conteudo da IA: '{capitulo.content}'")
print(f"Gerado por IA: {capitulo.ai_generated}")

print()

# ==================================================
# Secao 3: Properties vs metodos
# ==================================================
print("=" * 50)
print("SECAO 3: Properties vs metodos")
print("=" * 50)

# Uma property parece um atributo, mas executa codigo por tras.
# Usamos SEM parenteses: objeto.property (nao objeto.property())
# Metodos usamos COM parenteses: objeto.metodo()

# Property is_valid_email - parece atributo, mas calcula o resultado
print(f"Email do usuario: {usuario.email}")
print(f"Email valido? {usuario.is_valid_email}")  # Sem parenteses!

# Criando usuario com email invalido (sem @)
usuario_sem_arroba = User(
    id=3,
    email="email_invalido",
    name="Teste",
    hashed_password="xxx",
    created_at=datetime.now(UTC),
)
print(f"\nEmail: {usuario_sem_arroba.email}")
print(f"Email valido? {usuario_sem_arroba.is_valid_email}")

# Property word_count - conta palavras automaticamente
capitulo_longo = Chapter(
    id=2,
    project_id=1,
    title="Capitulo Grande",
    content="Este e um capitulo com varias palavras para demonstrar a contagem",
    created_at=datetime.now(UTC),
)
print(f"\nConteudo: '{capitulo_longo.content}'")
print(f"Palavras: {capitulo_longo.word_count}")  # Sem parenteses!

# Capitulo vazio tem 0 palavras
capitulo_vazio = Chapter(
    id=3,
    project_id=1,
    title="Capitulo Vazio",
    created_at=datetime.now(UTC),
)
print(f"Capitulo vazio - Palavras: {capitulo_vazio.word_count}")

print()

# ==================================================
# Secao 4: Enums - estados controlados
# ==================================================
print("=" * 50)
print("SECAO 4: Enums - estados controlados")
print("=" * 50)

# Enum define um conjunto FIXO de valores possiveis.
# E muito melhor que usar strings livres - evita erros de digitacao!

# Listando todos os status possiveis
print("Status possiveis de um projeto:")
for status in ProjectStatus:
    print(f"  - {status.name} = '{status.value}'")

# Comparando enums
projeto_novo = Project(
    id=2,
    user_id=1,
    title="Outro Ebook",
    created_at=datetime.now(UTC),
)

print(f"\nProjeto novo esta em DRAFT? {projeto_novo.status == ProjectStatus.DRAFT}")
print(f"Projeto novo esta COMPLETED? {projeto_novo.status == ProjectStatus.COMPLETED}")

# Acessando nome e valor do enum
print(f"\nNome do enum: {projeto_novo.status.name}")
print(f"Valor do enum: {projeto_novo.status.value}")

# Criando enum a partir do valor (string)
status_from_string = ProjectStatus("in_progress")
print(f"\nEnum criado a partir de string: {status_from_string}")

print()

# ==================================================
# Secao 5: Composicao - objetos que se relacionam
# ==================================================
print("=" * 50)
print("SECAO 5: Composicao - objetos que se relacionam")
print("=" * 50)

# Composicao = objetos que contem ou referenciam outros objetos.
# No nosso sistema: User -> Project -> Chapter
# Um usuario tem varios projetos, um projeto tem varios capitulos.

# Criando um cenario completo
autor = User(
    id=1,
    email="autor@ebook.com",
    name="Maria Escritora",
    hashed_password="hash_seguro",
    created_at=datetime.now(UTC),
)

# Projeto pertence ao autor (via user_id)
ebook = Project(
    id=1,
    user_id=autor.id,
    title="Aprendendo Python",
    description="Guia completo para iniciantes",
    created_at=datetime.now(UTC),
)

# Capitulos pertencem ao projeto (via project_id)
capitulos = [
    Chapter(
        id=1,
        project_id=ebook.id,
        title="Introducao ao Python",
        content="Python foi criado por Guido van Rossum em 1991.",
        order=0,
        created_at=datetime.now(UTC),
    ),
    Chapter(
        id=2,
        project_id=ebook.id,
        title="Variaveis e Tipos",
        content="Em Python, variaveis sao criadas na primeira atribuicao.",
        order=1,
        created_at=datetime.now(UTC),
    ),
    Chapter(
        id=3,
        project_id=ebook.id,
        title="Funcoes",
        content="Funcoes sao blocos de codigo reutilizaveis definidos com def.",
        order=2,
        created_at=datetime.now(UTC),
    ),
]

# Mostrando a hierarquia
print(f"Autor: {autor.name} ({autor.email})")
print(f"Projeto: {ebook.title}")
print(f"Descricao: {ebook.description}")
print(f"Status: {ebook.status.value}")
print(f"\nCapitulos ({len(capitulos)} total):")

total_palavras = 0
for cap in capitulos:
    print(f"  {cap.order + 1}. {cap.title} ({cap.word_count} palavras)")
    total_palavras += cap.word_count

print(f"\nTotal de palavras no ebook: {total_palavras}")

# Simulando o fluxo de trabalho
print("\n--- Simulando fluxo de trabalho ---")
ebook.mark_in_progress()
print(f"Projeto marcado como: {ebook.status.value}")

# Gerando conteudo por IA para o ultimo capitulo
capitulos[2].update_content(
    "Funcoes sao blocos de codigo reutilizaveis. "
    "Use def para definir uma funcao. "
    "Funcoes podem receber parametros e retornar valores.",
    from_ai=True,
)
print(f"Capitulo '{capitulos[2].title}' atualizado por IA")
print(f"  Novo conteudo: {capitulos[2].word_count} palavras")
print(f"  Gerado por IA: {capitulos[2].ai_generated}")

ebook.mark_completed()
print(f"Projeto finalizado: {ebook.status.value}")

print()
print("=" * 50)
print("FIM DA DEMONSTRACAO - Aula 01")
print("=" * 50)
