"""
Repositorio de Projetos (ProjectRepository)

Contem TODAS as operacoes de banco para projetos de ebook.
Segue o mesmo padrao do UserRepository: uma classe autocontida
com operacoes CRUD basicas + queries especificas de negocio.

Conceitos ensinados neste arquivo:
- joinedload(): carregamento "ansioso" (eager loading) de relacionamentos
  Em vez de fazer 1 query por capitulo (N+1 problem), faz 1 unica query com JOIN
- ilike(): busca case-insensitive (LIKE no SQL, mas ignora maiusculas/minusculas)
- Filtros compostos: combinar multiplas condicoes com .filter(cond1, cond2)
- Ordenacao: order_by() com desc() para ordem decrescente

CONCEITO IMPORTANTE - Eager vs Lazy Loading:
=============================================
Por padrao, SQLAlchemy usa "lazy loading" nos relacionamentos.
Isso significa que ao buscar um Project, os capitulos NAO sao carregados:

    project = repo.get_by_id(1)
    # Os capitulos ainda NAO estao carregados!
    # So serao carregados quando voce acessar project.chapters
    # Isso causa uma NOVA query ao banco (N+1 problem)

Com "eager loading" (joinedload), carregamos tudo de uma vez:

    project = repo.get_with_chapters(1)
    # Os capitulos JA estao carregados!
    # Nenhuma query extra ao acessar project.chapters

Regra pratica:
- Se voce vai usar o relacionamento: use eager loading (1 query)
- Se talvez nao vai usar: deixe lazy (evita carregar dados desnecessarios)

Para rodar: Importar via app.repositories
    from app.repositories import ProjectRepository
"""

from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models.project import Project


class ProjectRepository:
    """Repositorio com todas as operacoes de banco para projetos.

    Metodos CRUD (operacoes basicas):
    - get_by_id(id) -> Project | None
    - get_all(skip, limit) -> list[Project]
    - create(project) -> Project
    - update(project) -> Project
    - delete(project) -> None
    - count() -> int

    Metodos especificos de projeto:
    - get_by_user(user_id) -> list[Project]
    - get_by_user_and_status(user_id, status) -> list[Project]
    - get_with_chapters(project_id) -> Project | None
    - search_by_title(user_id, search) -> list[Project]
    - count_by_user(user_id) -> int

    Exemplo de uso:
        db = session_factory()
        repo = ProjectRepository(db)
        projects = repo.get_by_user(user_id=1)
    """

    def __init__(self, db: Session) -> None:
        """Inicializa o repositorio com a sessao do banco.

        Args:
            db: Sessao do SQLAlchemy.
        """
        self.db = db

    # =========================================================
    # CRUD - Operacoes basicas (Create, Read, Update, Delete)
    # =========================================================

    def get_by_id(self, id: int) -> Project | None:
        """Busca um projeto pelo ID (chave primaria).

        Usa db.get() do SQLAlchemy 2.0 - a forma moderna e recomendada.

        Args:
            id: O identificador unico do projeto.

        Returns:
            O Project encontrado ou None se nao existir.

        Exemplo:
            project = repo.get_by_id(1)
            if project:
                print(project.title)
        """
        return self.db.get(Project, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Project]:
        """Lista projetos com paginacao (skip/limit).

        NUNCA retorne todos os registros sem limite! Em producao, uma tabela
        pode ter milhoes de linhas. Sempre use paginacao.

        Args:
            skip: Quantos registros pular (offset). Default: 0.
            limit: Maximo de registros a retornar. Default: 100.

        Returns:
            Lista de projetos.
        """
        return self.db.query(Project).offset(skip).limit(limit).all()

    def create(self, project: Project) -> Project:
        """Cria um novo projeto no banco.

        Fluxo:
        1. db.add(project): marca o projeto para insercao
        2. db.commit(): envia o INSERT para o banco
        3. db.refresh(project): recarrega com dados do banco (id, created_at)

        Args:
            project: Instancia do Project a ser salva.

        Returns:
            O mesmo objeto, agora com id e campos preenchidos pelo banco.

        Exemplo:
            project = Project(user_id=1, title="Meu Ebook")
            project = repo.create(project)
            print(project.id)  # Agora tem um ID!
        """
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        """Atualiza um projeto existente no banco.

        O SQLAlchemy rastreia mudancas automaticamente (dirty tracking).
        Basta modificar os atributos do objeto e chamar commit().

        Args:
            project: Instancia do Project com atributos modificados.

        Returns:
            O projeto atualizado com dados frescos do banco.

        Exemplo:
            project = repo.get_by_id(1)
            project.title = "Novo Titulo"
            project = repo.update(project)
        """
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        """Remove um projeto do banco.

        CUIDADO: Esta operacao e irreversivel apos o commit!
        Devido ao cascade="all, delete-orphan" no modelo,
        deletar um projeto TAMBEM deleta todos os seus capitulos.

        Args:
            project: Instancia do Project a ser removida.
        """
        self.db.delete(project)
        self.db.commit()

    def count(self) -> int:
        """Conta o total de projetos no banco.

        Returns:
            Numero total de projetos.
        """
        return self.db.query(Project).count()

    # =========================================================
    # Queries especificas de projeto
    # =========================================================

    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Project]:
        """Lista projetos de um usuario especifico.

        IMPORTANTE: Sempre filtrar por user_id! Um usuario NAO pode
        ver projetos de outro usuario. Este padrao e fundamental
        para seguranca em aplicacoes multi-usuario.

        Ordena por created_at decrescente (mais recente primeiro),
        que e o comportamento esperado pelo usuario.

        Args:
            user_id: ID do usuario dono dos projetos.
            skip: Quantos registros pular (paginacao).
            limit: Maximo de registros a retornar.

        Returns:
            Lista de projetos do usuario.

        Exemplo:
            # Listar projetos do usuario 1
            projetos = repo.get_by_user(user_id=1)
        """
        return (
            self.db.query(Project)
            .filter(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_status(
        self, user_id: int, status: str
    ) -> list[Project]:
        """Lista projetos de um usuario filtrados por status.

        Exemplo de filtro composto: combina user_id E status.
        No SQL, isso gera: WHERE user_id = ? AND status = ?

        Quando passamos multiplas condicoes para .filter(), o SQLAlchemy
        combina com AND automaticamente. Exemplo:
            .filter(Project.user_id == 1, Project.status == "draft")
            -> SQL: WHERE user_id = 1 AND status = 'draft'

        Args:
            user_id: ID do usuario dono dos projetos.
            status: Status desejado (ex: "draft", "in_progress", "completed").

        Returns:
            Lista de projetos do usuario com o status especificado.

        Exemplo:
            # Listar rascunhos do usuario 1
            rascunhos = repo.get_by_user_and_status(user_id=1, status="draft")
        """
        return (
            self.db.query(Project)
            .filter(
                Project.user_id == user_id,
                Project.status == status,
            )
            .order_by(Project.created_at.desc())
            .all()
        )

    def get_with_chapters(self, project_id: int) -> Project | None:
        """Busca um projeto com seus capitulos carregados (eager loading).

        CONCEITO CHAVE - Eager vs Lazy Loading:

        SEM joinedload (lazy - padrao):
            project = repo.get_by_id(1)     # 1 query: SELECT * FROM projects
            for ch in project.chapters:      # N queries: SELECT * FROM chapters
                print(ch.title)              #   WHERE project_id = 1 (para cada!)
            # Total: 1 + N queries (RUIM para performance!)

        COM joinedload (eager):
            project = repo.get_with_chapters(1)  # 1 query com JOIN
            for ch in project.chapters:           # Sem query extra!
                print(ch.title)                   # Dados ja estao em memoria
            # Total: 1 query (BOM!)

        joinedload vem de sqlalchemy.orm e gera um LEFT JOIN no SQL:
            SELECT projects.*, chapters.*
            FROM projects
            LEFT JOIN chapters ON chapters.project_id = projects.id
            WHERE projects.id = ?

        Args:
            project_id: ID do projeto a buscar.

        Returns:
            O Project com chapters carregados, ou None se nao existir.

        Exemplo:
            project = repo.get_with_chapters(1)
            if project:
                print(f"Projeto: {project.title}")
                for ch in project.chapters:
                    print(f"  Cap {ch.order}: {ch.title}")
        """
        return (
            self.db.query(Project)
            .options(joinedload(Project.chapters))
            .filter(Project.id == project_id)
            .first()
        )

    def search_by_title(self, user_id: int, search: str) -> list[Project]:
        """Pesquisa projetos de um usuario pelo titulo (case-insensitive).

        Usa ilike() para busca case-insensitive:
        - ilike = Insensitive LIKE (ignora maiusculas/minusculas)
        - O % e o coringa (wildcard) do SQL: qualquer sequencia de caracteres

        Exemplo de como funciona:
            search = "python"
            -> SQL: WHERE title ILIKE '%python%'
            -> Encontra: "Aprenda Python", "PYTHON Avancado", "Meu python book"

        NOTA: ilike() funciona nativamente no PostgreSQL.
        No SQLite, o LIKE ja e case-insensitive para ASCII por padrao,
        entao funciona tambem (mas so para caracteres ASCII, nao acentuados).

        Args:
            user_id: ID do usuario (seguranca: so busca nos projetos dele).
            search: Texto a procurar no titulo.

        Returns:
            Lista de projetos que contem o texto no titulo.

        Exemplo:
            # Buscar projetos com "python" no titulo
            resultados = repo.search_by_title(user_id=1, search="python")
        """
        return (
            self.db.query(Project)
            .filter(
                Project.user_id == user_id,
                Project.title.ilike(f"%{search}%"),
            )
            .order_by(Project.created_at.desc())
            .all()
        )

    def count_by_user(self, user_id: int) -> int:
        """Conta quantos projetos um usuario tem.

        Util para mostrar estatisticas no dashboard do usuario
        ou para verificar limites (ex: plano gratis = max 5 projetos).

        Args:
            user_id: ID do usuario.

        Returns:
            Numero de projetos do usuario.

        Exemplo:
            total = repo.count_by_user(user_id=1)
            if total >= 5:
                print("Limite de projetos atingido!")
        """
        return (
            self.db.query(Project)
            .filter(Project.user_id == user_id)
            .count()
        )
