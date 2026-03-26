"""
Repositorio Base Generico (BaseRepository)

O Repository Pattern e uma camada entre a logica de negocio e o acesso ao banco.
Em vez de escrever queries SQL diretamente no codigo da aplicacao, centralizamos
todas as operacoes de banco aqui. Isso traz varias vantagens:

1. SEPARACAO DE RESPONSABILIDADES: a logica de negocio nao precisa saber
   como os dados sao armazenados (SQL, NoSQL, arquivo, API...).

2. REUTILIZACAO: operacoes comuns (criar, buscar, deletar) ficam na classe
   base e sao herdadas por todos os repositorios concretos.

3. TESTABILIDADE: podemos substituir o repositorio real por um fake nos testes,
   sem mudar a logica de negocio.

Conceitos ensinados:
- Generic[T]: permite criar uma classe que funciona com qualquer tipo
- TypeVar: variavel de tipo - placeholder para o tipo concreto
- Session do SQLAlchemy: a "conversa" com o banco de dados
- CRUD: Create, Read, Update, Delete - as 4 operacoes basicas

Para rodar: Este modulo e importado por repositorios concretos (UserRepository, etc.)
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

# TypeVar cria uma "variavel de tipo" - um placeholder que sera substituido
# pelo tipo concreto quando a classe for herdada.
#
# Exemplo:
#   BaseRepository[User]  -> ModelType vira User
#   BaseRepository[Project] -> ModelType vira Project
#
# Isso permite que o Python (e ferramentas como mypy/pyright) saibam
# exatamente qual tipo de objeto o repositorio manipula.
ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Repositorio base com operacoes CRUD genericas.

    Esta classe encapsula as operacoes mais comuns de banco de dados.
    Repositorios concretos herdam dela e adicionam queries especificas.

    Generic[ModelType] significa que esta classe e "generica" - funciona
    com qualquer modelo SQLAlchemy. O tipo concreto e definido na heranca:

        class UserRepository(BaseRepository[User]):
            ...  # ModelType = User automaticamente

    Atributos:
        model: A classe do modelo SQLAlchemy (ex: User, Project)
        db: A sessao do SQLAlchemy para executar operacoes no banco

    Exemplo de uso:
        db = session_factory()
        repo = BaseRepository(User, db)
        user = repo.get_by_id(1)
    """

    def __init__(self, model: type[ModelType], db: Session) -> None:
        """Inicializa o repositorio com o modelo e a sessao do banco.

        Args:
            model: A classe do modelo (ex: User, Project, Chapter).
                   Usamos type[ModelType] porque passamos a CLASSE, nao uma instancia.
            db: Sessao do SQLAlchemy para executar queries.
        """
        self.model = model
        self.db = db

    # --- READ (Leitura) ---

    def get_by_id(self, id: int) -> ModelType | None:
        """Busca um registro pelo ID (chave primaria).

        Usa db.get() do SQLAlchemy 2.0 - a forma moderna e recomendada.
        O antigo db.query(Model).get(id) esta deprecated (nao usar!).

        Args:
            id: O identificador unico do registro.

        Returns:
            O objeto encontrado ou None se nao existir.

        Exemplo:
            user = repo.get_by_id(1)
            if user:
                print(user.name)
        """
        return self.db.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Lista registros com paginacao (skip/limit).

        NUNCA retorne todos os registros sem limite! Em producao, uma tabela
        pode ter milhoes de linhas. Sempre use paginacao.

        Args:
            skip: Quantos registros pular (offset). Default: 0.
            limit: Maximo de registros a retornar. Default: 100.

        Returns:
            Lista de objetos do modelo.

        Exemplo:
            # Primeira pagina (10 primeiros)
            users = repo.get_all(skip=0, limit=10)

            # Segunda pagina (10 seguintes)
            users = repo.get_all(skip=10, limit=10)
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def count(self) -> int:
        """Conta o total de registros na tabela.

        Util para paginacao (saber quantas paginas existem)
        e para dashboards/relatorios.

        Returns:
            Numero total de registros.

        Exemplo:
            total = repo.count()
            print(f"Total de usuarios: {total}")
        """
        return self.db.query(self.model).count()

    # --- CREATE (Criacao) ---

    def create(self, obj: ModelType) -> ModelType:
        """Cria um novo registro no banco.

        Fluxo:
        1. db.add(obj): marca o objeto para insercao
        2. db.commit(): envia o INSERT para o banco
        3. db.refresh(obj): recarrega o objeto com dados do banco
           (ex: id gerado, created_at preenchido pelo servidor)

        NOTA: Em projetos maiores, o commit seria responsabilidade
        de uma camada superior (Unit of Work pattern). Aqui simplificamos
        para fins didaticos - cada operacao faz seu proprio commit.

        Args:
            obj: Instancia do modelo a ser salva.

        Returns:
            O mesmo objeto, agora com id e campos preenchidos pelo banco.

        Exemplo:
            user = User(email="joao@email.com", name="Joao", hashed_password="hash")
            user = repo.create(user)
            print(user.id)  # Agora tem um ID!
        """
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- UPDATE (Atualizacao) ---

    def update(self, obj: ModelType) -> ModelType:
        """Atualiza um registro existente no banco.

        O SQLAlchemy rastreia mudancas automaticamente (dirty tracking).
        Basta modificar os atributos do objeto e chamar commit().

        Fluxo:
        1. Modifique o objeto: user.name = "Novo Nome"
        2. Chame repo.update(user)
        3. O SQLAlchemy detecta a mudanca e gera o UPDATE SQL

        Args:
            obj: Instancia do modelo com atributos modificados.

        Returns:
            O objeto atualizado com dados frescos do banco.

        Exemplo:
            user = repo.get_by_id(1)
            user.name = "Novo Nome"
            user = repo.update(user)
        """
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- DELETE (Exclusao) ---

    def delete(self, obj: ModelType) -> None:
        """Remove um registro do banco.

        CUIDADO: Esta operacao e irreversivel apos o commit!
        Em producao, muitas vezes preferimos "soft delete"
        (marcar como inativo) em vez de deletar de verdade.

        Args:
            obj: Instancia do modelo a ser removida.

        Exemplo:
            user = repo.get_by_id(1)
            if user:
                repo.delete(user)
        """
        self.db.delete(obj)
        self.db.commit()
