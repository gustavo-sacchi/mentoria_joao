"""
Repositorio de Usuarios (UserRepository)

O Repository Pattern e uma camada entre a logica de negocio e o acesso ao banco.
Em vez de escrever queries SQL diretamente no codigo da aplicacao, centralizamos
todas as operacoes de banco aqui. Isso traz varias vantagens:

1. SEPARACAO DE RESPONSABILIDADES: a logica de negocio nao precisa saber
   como os dados sao armazenados (SQL, NoSQL, arquivo, API...).

2. REUTILIZACAO: se precisar buscar um usuario em varios lugares do codigo,
   basta chamar repo.get_by_email() em vez de repetir a query.

3. TESTABILIDADE: podemos substituir o repositorio real por um fake nos testes,
   sem mudar a logica de negocio.

Conceitos ensinados:
- Session do SQLAlchemy: a "conversa" com o banco de dados
- CRUD: Create, Read, Update, Delete - as 4 operacoes basicas
- Filtros SQLAlchemy: como usar .filter() com operadores Python
- Operator overload: User.email == "x" NAO e comparacao Python,
  e o SQLAlchemy gerando SQL WHERE email = 'x'

Para rodar: Importar via app.repositories
    from app.repositories import UserRepository
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repositorio com todas as operacoes de banco para usuarios.

    Esta classe contem TODAS as operacoes que precisamos para manipular
    usuarios no banco: as operacoes CRUD basicas (criar, ler, atualizar,
    deletar) e tambem queries especificas de usuario (buscar por email,
    listar ativos, etc).

    Metodos CRUD (operacoes basicas):
    - get_by_id(id) -> User | None
    - get_all(skip, limit) -> list[User]
    - create(user) -> User
    - update(user) -> User
    - delete(user) -> None
    - count() -> int

    Metodos especificos de usuario:
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
        """Inicializa o repositorio com a sessao do banco.

        A sessao (Session) e a "conversa" com o banco de dados.
        Toda operacao de leitura ou escrita precisa de uma sessao.

        Args:
            db: Sessao do SQLAlchemy.
        """
        self.db = db

    # =========================================================
    # CRUD - Operacoes basicas (Create, Read, Update, Delete)
    # =========================================================

    def get_by_id(self, id: int) -> User | None:
        """Busca um usuario pelo ID (chave primaria).

        Usa db.get() do SQLAlchemy 2.0 - a forma moderna e recomendada.
        O antigo db.query(Model).get(id) esta deprecated (nao usar!).

        Args:
            id: O identificador unico do usuario.

        Returns:
            O User encontrado ou None se nao existir.

        Exemplo:
            user = repo.get_by_id(1)
            if user:
                print(user.name)
        """
        return self.db.get(User, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista usuarios com paginacao (skip/limit).

        NUNCA retorne todos os registros sem limite! Em producao, uma tabela
        pode ter milhoes de linhas. Sempre use paginacao.

        Args:
            skip: Quantos registros pular (offset). Default: 0.
            limit: Maximo de registros a retornar. Default: 100.

        Returns:
            Lista de usuarios.

        Exemplo:
            # Primeira pagina (10 primeiros)
            users = repo.get_all(skip=0, limit=10)

            # Segunda pagina (10 seguintes)
            users = repo.get_all(skip=10, limit=10)
        """
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user: User) -> User:
        """Cria um novo usuario no banco.

        Fluxo:
        1. db.add(user): marca o usuario para insercao
        2. db.commit(): envia o INSERT para o banco
        3. db.refresh(user): recarrega o objeto com dados do banco
           (ex: id gerado, created_at preenchido pelo servidor)

        NOTA: Em projetos maiores, o commit seria responsabilidade
        de uma camada superior (Unit of Work pattern). Aqui simplificamos
        para fins didaticos - cada operacao faz seu proprio commit.

        Args:
            user: Instancia do User a ser salva.

        Returns:
            O mesmo objeto, agora com id e campos preenchidos pelo banco.

        Exemplo:
            user = User(email="joao@email.com", name="Joao", hashed_password="hash")
            user = repo.create(user)
            print(user.id)  # Agora tem um ID!
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Atualiza um usuario existente no banco.

        O SQLAlchemy rastreia mudancas automaticamente (dirty tracking).
        Basta modificar os atributos do objeto e chamar commit().

        Fluxo:
        1. Modifique o objeto: user.name = "Novo Nome"
        2. Chame repo.update(user)
        3. O SQLAlchemy detecta a mudanca e gera o UPDATE SQL

        Args:
            user: Instancia do User com atributos modificados.

        Returns:
            O usuario atualizado com dados frescos do banco.

        Exemplo:
            user = repo.get_by_id(1)
            user.name = "Novo Nome"
            user = repo.update(user)
        """
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Remove um usuario do banco.

        CUIDADO: Esta operacao e irreversivel apos o commit!
        Em producao, muitas vezes preferimos "soft delete"
        (marcar como inativo) em vez de deletar de verdade.
        Veja o metodo deactivate() para soft delete.

        Args:
            user: Instancia do User a ser removida.

        Exemplo:
            user = repo.get_by_id(1)
            if user:
                repo.delete(user)
        """
        self.db.delete(user)
        self.db.commit()

    def count(self) -> int:
        """Conta o total de usuarios no banco.

        Util para paginacao (saber quantas paginas existem)
        e para dashboards/relatorios.

        Returns:
            Numero total de usuarios.

        Exemplo:
            total = repo.count()
            print(f"Total de usuarios: {total}")
        """
        return self.db.query(User).count()

    # =========================================================
    # Queries especificas de usuario
    # =========================================================

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
