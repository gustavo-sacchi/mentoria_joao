"""
Repositorio de Usuarios (UserRepository)

Este repositorio herda do BaseRepository e adiciona queries especificas
para a entidade User. Enquanto o BaseRepository tem operacoes genericas
(get_by_id, create, delete...), o UserRepository sabe fazer buscas
que so fazem sentido para usuarios (buscar por email, listar ativos...).

Conceitos ensinados:
- Heranca pratica: UserRepository herda TODOS os metodos do BaseRepository
- Especializacao: adiciona metodos que so existem para User
- Filtros SQLAlchemy: como usar .filter() com operadores Python
- Operator overload: User.email == "x" NAO e comparacao Python,
  e o SQLAlchemy gerando SQL WHERE email = 'x'

Para rodar: Importar via app.repositories
    from app.repositories import UserRepository
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio especializado para operacoes com usuarios.

    Herda de BaseRepository[User], o que significa:
    - ModelType = User (o generico foi "preenchido")
    - Todos os metodos CRUD do BaseRepository funcionam com User
    - Podemos adicionar metodos especificos de usuario

    Metodos herdados (do BaseRepository):
    - get_by_id(id) -> User | None
    - get_all(skip, limit) -> list[User]
    - create(user) -> User
    - update(user) -> User
    - delete(user) -> None
    - count() -> int

    Metodos proprios (definidos aqui):
    - get_by_email(email) -> User | None
    - get_active_users(skip, limit) -> list[User]
    - deactivate(user) -> User
    - email_exists(email) -> bool

    Exemplo de uso:
        db = session_factory()
        repo = UserRepository(db)
        user = repo.get_by_email("joao@email.com")
    """

    def __init__(self, db: Session) -> None:
        """Inicializa o UserRepository com a sessao do banco.

        Diferente do BaseRepository que recebe model e db,
        aqui ja sabemos que o modelo e User - entao o __init__
        so precisa receber a sessao.

        O super().__init__(User, db) chama o construtor do pai
        passando a classe User automaticamente.

        Args:
            db: Sessao do SQLAlchemy.
        """
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        """Busca um usuario pelo email.

        IMPORTANTE sobre o operador ==:
        Quando escrevemos User.email == email, o Python NAO esta
        comparando strings! O SQLAlchemy usa "operator overloading"
        para transformar isso em SQL:

            User.email == "joao@email.com"
            -> SQL: WHERE users.email = 'joao@email.com'

        .first() retorna o primeiro resultado ou None se nao encontrar.
        Como email e unique, so pode haver no maximo 1 resultado.

        Args:
            email: O email do usuario a buscar.

        Returns:
            O User encontrado ou None.

        Exemplo:
            user = repo.get_by_email("joao@email.com")
            if user:
                print(f"Encontrado: {user.name}")
            else:
                print("Usuario nao encontrado")
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista apenas usuarios ativos (is_active=True).

        Filtra usando User.is_active == True. Note que usamos == (operador
        SQLAlchemy) e NAO "is True" (operador Python). O "is" verifica
        identidade de objetos em Python, mas o == do SQLAlchemy gera SQL.

        NOTA sobre o warning do linter:
        Ferramentas como ruff podem reclamar de "== True" dizendo para
        usar "is True". Neste caso, ignore o aviso - com SQLAlchemy
        DEVEMOS usar == para gerar o SQL correto.

        Args:
            skip: Quantos registros pular (paginacao).
            limit: Maximo de registros a retornar.

        Returns:
            Lista de usuarios ativos.

        Exemplo:
            ativos = repo.get_active_users()
            print(f"{len(ativos)} usuarios ativos")
        """
        return (
            self.db.query(User)
            .filter(User.is_active == True)  # noqa: E712 - SQLAlchemy requer ==
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate(self, user: User) -> User:
        """Desativa um usuario (soft delete).

        Em vez de deletar o registro do banco (hard delete),
        apenas marcamos como inativo. Isso preserva o historico
        e permite reativar o usuario no futuro.

        Fluxo:
        1. Muda is_active para False
        2. Salva no banco (commit)
        3. Recarrega o objeto (refresh)

        Args:
            user: O usuario a ser desativado.

        Returns:
            O usuario atualizado com is_active=False.

        Exemplo:
            user = repo.get_by_email("joao@email.com")
            if user:
                user = repo.deactivate(user)
                print(f"Usuario {user.name} desativado")
        """
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user

    def email_exists(self, email: str) -> bool:
        """Verifica se um email ja esta cadastrado.

        Util antes de criar um novo usuario, para evitar emails duplicados.
        Usa .count() que retorna o numero de registros que atendem o filtro.

        Por que usar count() ao inves de get_by_email()?
        - count() e mais eficiente: o banco conta sem carregar o objeto inteiro
        - Retorna bool diretamente, semantica mais clara para verificacao

        Args:
            email: O email a verificar.

        Returns:
            True se o email ja existe, False caso contrario.

        Exemplo:
            if repo.email_exists("joao@email.com"):
                print("Email ja cadastrado!")
            else:
                print("Email disponivel")
        """
        return self.db.query(User).filter(User.email == email).count() > 0
