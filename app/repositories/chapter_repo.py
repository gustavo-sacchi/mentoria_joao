"""
Repositorio de Capitulos (ChapterRepository)

Contem TODAS as operacoes de banco para capitulos de ebook.
Segue o mesmo padrao do UserRepository e ProjectRepository:
uma classe autocontida com CRUD basico + queries especificas.

Conceitos ensinados neste arquivo:
- func.max(): funcao de agregacao do SQL (pega o maior valor)
- func.coalesce(): retorna o primeiro valor NAO nulo de uma lista
  Exemplo: COALESCE(MAX(order), 0) -> se nao tem capitulos, retorna 0
- Ordenacao com order_by(): definir a ordem dos resultados
- Filtros com booleanos: ai_generated == True no SQLAlchemy

CONCEITO IMPORTANTE - Ordenacao de Capitulos:
=============================================
Um ebook tem capitulos em uma ordem especifica (Cap 1, Cap 2, Cap 3...).
A coluna 'order' na tabela chapters guarda essa posicao.

Quando adicionamos um novo capitulo, precisamos saber qual e a proxima
posicao disponivel. O metodo get_next_order() faz isso:

    # Se o projeto tem capitulos com order 1, 2, 3:
    next_order = repo.get_next_order(project_id=1)  # Retorna 4

    # Se o projeto nao tem capitulos:
    next_order = repo.get_next_order(project_id=99)  # Retorna 1

Isso usa func.max() e func.coalesce() do SQLAlchemy, que geram SQL:
    SELECT COALESCE(MAX(chapters.order), 0) FROM chapters WHERE project_id = ?

Para rodar: Importar via app.repositories
    from app.repositories import ChapterRepository
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chapter import Chapter


class ChapterRepository:
    """Repositorio com todas as operacoes de banco para capitulos.

    Metodos CRUD (operacoes basicas):
    - get_by_id(id) -> Chapter | None
    - get_all(skip, limit) -> list[Chapter]
    - create(chapter) -> Chapter
    - update(chapter) -> Chapter
    - delete(chapter) -> None
    - count() -> int

    Metodos especificos de capitulo:
    - get_by_project(project_id) -> list[Chapter]
    - get_by_project_ordered(project_id) -> list[Chapter]
    - get_ai_generated(project_id) -> list[Chapter]
    - get_next_order(project_id) -> int
    - reorder(chapter, new_order) -> None

    Exemplo de uso:
        db = session_factory()
        repo = ChapterRepository(db)
        chapters = repo.get_by_project(project_id=1)
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

    def get_by_id(self, id: int) -> Chapter | None:
        """Busca um capitulo pelo ID (chave primaria).

        Args:
            id: O identificador unico do capitulo.

        Returns:
            O Chapter encontrado ou None se nao existir.

        Exemplo:
            chapter = repo.get_by_id(1)
            if chapter:
                print(chapter.title)
        """
        return self.db.get(Chapter, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Chapter]:
        """Lista capitulos com paginacao (skip/limit).

        Args:
            skip: Quantos registros pular (offset). Default: 0.
            limit: Maximo de registros a retornar. Default: 100.

        Returns:
            Lista de capitulos.
        """
        return self.db.query(Chapter).offset(skip).limit(limit).all()

    def create(self, chapter: Chapter) -> Chapter:
        """Cria um novo capitulo no banco.

        Fluxo:
        1. db.add(chapter): marca o capitulo para insercao
        2. db.commit(): envia o INSERT para o banco
        3. db.refresh(chapter): recarrega com dados do banco (id, created_at)

        Args:
            chapter: Instancia do Chapter a ser salva.

        Returns:
            O mesmo objeto, agora com id e campos preenchidos pelo banco.

        Exemplo:
            chapter = Chapter(project_id=1, title="Introducao", order=1)
            chapter = repo.create(chapter)
            print(chapter.id)  # Agora tem um ID!
        """
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def update(self, chapter: Chapter) -> Chapter:
        """Atualiza um capitulo existente no banco.

        O SQLAlchemy rastreia mudancas automaticamente (dirty tracking).
        Basta modificar os atributos do objeto e chamar commit().

        Args:
            chapter: Instancia do Chapter com atributos modificados.

        Returns:
            O capitulo atualizado com dados frescos do banco.

        Exemplo:
            chapter = repo.get_by_id(1)
            chapter.title = "Novo Titulo"
            chapter = repo.update(chapter)
        """
        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def delete(self, chapter: Chapter) -> None:
        """Remove um capitulo do banco.

        CUIDADO: Esta operacao e irreversivel apos o commit!

        Args:
            chapter: Instancia do Chapter a ser removida.
        """
        self.db.delete(chapter)
        self.db.commit()

    def count(self) -> int:
        """Conta o total de capitulos no banco.

        Returns:
            Numero total de capitulos.
        """
        return self.db.query(Chapter).count()

    # =========================================================
    # Queries especificas de capitulo
    # =========================================================

    def get_by_project(self, project_id: int) -> list[Chapter]:
        """Lista capitulos de um projeto, ordenados pela posicao (order).

        A ordenacao e ASC (crescente): Cap 1, Cap 2, Cap 3...
        Isso reflete a ordem natural de leitura do ebook.

        Args:
            project_id: ID do projeto.

        Returns:
            Lista de capitulos ordenados pela coluna 'order'.

        Exemplo:
            chapters = repo.get_by_project(project_id=1)
            for ch in chapters:
                print(f"  Cap {ch.order}: {ch.title}")
        """
        return (
            self.db.query(Chapter)
            .filter(Chapter.project_id == project_id)
            .order_by(Chapter.order)
            .all()
        )

    def get_by_project_ordered(self, project_id: int) -> list[Chapter]:
        """Lista capitulos de um projeto ordenados por posicao.

        Este metodo e um ALIAS didatico de get_by_project().
        Ambos fazem a mesma coisa, mas o nome "ordered" deixa
        explicita a intencao de que os resultados vem ordenados.

        Em projetos reais, e comum ter metodos com nomes
        descritivos que deixam claro o que esta acontecendo,
        mesmo que internamente facam a mesma query.

        Args:
            project_id: ID do projeto.

        Returns:
            Lista de capitulos ordenados pela coluna 'order'.
        """
        return self.get_by_project(project_id)

    def get_ai_generated(self, project_id: int) -> list[Chapter]:
        """Lista capitulos gerados por IA de um projeto.

        Filtra por project_id E ai_generated == True.
        Util para saber quais capitulos foram escritos por IA
        vs quais foram escritos manualmente pelo usuario.

        NOTA sobre SQLAlchemy e booleanos:
        Usamos == True (com ==, nao 'is') porque o SQLAlchemy
        precisa do operador == para gerar o SQL correto.
        O linter pode reclamar - use '# noqa: E712' para silenciar.

        Args:
            project_id: ID do projeto.

        Returns:
            Lista de capitulos gerados por IA.

        Exemplo:
            ai_chapters = repo.get_ai_generated(project_id=1)
            print(f"{len(ai_chapters)} capitulos gerados por IA")
        """
        return (
            self.db.query(Chapter)
            .filter(
                Chapter.project_id == project_id,
                Chapter.ai_generated == True,  # noqa: E712 - SQLAlchemy requer ==
            )
            .order_by(Chapter.order)
            .all()
        )

    def get_next_order(self, project_id: int) -> int:
        """Calcula a proxima posicao disponivel para um capitulo.

        Usa func.max() e func.coalesce() do SQLAlchemy para fazer
        isso em uma unica query SQL, sem precisar carregar todos
        os capitulos em memoria.

        Como funciona:
        1. func.max(Chapter.order): pega o maior valor de 'order'
           - Se tem capitulos com order 1, 2, 3 -> retorna 3
           - Se NAO tem capitulos -> retorna NULL

        2. func.coalesce(valor, fallback): retorna o primeiro nao-nulo
           - coalesce(3, 0) -> retorna 3
           - coalesce(NULL, 0) -> retorna 0

        3. Somamos + 1 para obter a proxima posicao

        SQL gerado:
            SELECT COALESCE(MAX(chapters."order"), 0)
            FROM chapters
            WHERE chapters.project_id = ?

        Args:
            project_id: ID do projeto.

        Returns:
            A proxima posicao disponivel (1 se o projeto esta vazio).

        Exemplo:
            next_pos = repo.get_next_order(project_id=1)
            new_chapter = Chapter(project_id=1, title="Novo", order=next_pos)
        """
        result = (
            self.db.query(func.coalesce(func.max(Chapter.order), 0))
            .filter(Chapter.project_id == project_id)
            .scalar()
        )
        # result e um int (gracias ao coalesce, nunca sera None)
        return result + 1

    def reorder(self, chapter: Chapter, new_order: int) -> None:
        """Muda a posicao de um capitulo no ebook.

        Versao simplificada: apenas atualiza o campo 'order' do capitulo.

        NOTA PARA PRODUCAO: Em um sistema real, reordenar capitulos
        e mais complexo. Seria necessario ajustar a ordem de TODOS
        os capitulos afetados. Por exemplo, mover o Cap 5 para a
        posicao 2 precisaria empurrar os Caps 2, 3 e 4 para frente.

        Para este projeto didatico, mantemos a logica simples:
        apenas setar o novo valor de order.

        Args:
            chapter: O capitulo a ser reposicionado.
            new_order: A nova posicao desejada.

        Exemplo:
            chapter = repo.get_by_id(1)
            repo.reorder(chapter, new_order=3)
        """
        chapter.order = new_order
        self.db.commit()
        self.db.refresh(chapter)
