"""
Modelo de dominio: User (Usuario)

Classe Python pura usando dataclass para representar um usuario do sistema.
Nesta fase nao usamos banco de dados - apenas OOP puro.

Conceitos ensinados:
- dataclass com slots=True
- Type hints modernos (int | None)
- Metodo __post_init__ para validacao
- Metodo __repr__ customizado
- Property (metodo que parece atributo)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    """Representa um usuario do sistema de ebooks.

    Atributos:
        id: Identificador unico (None quando ainda nao foi salvo no banco)
        email: Email do usuario (deve conter @)
        name: Nome completo do usuario
        hashed_password: Senha ja criptografada (nunca armazene senha em texto!)
        created_at: Data/hora de criacao da conta
        is_active: Se o usuario esta ativo no sistema
    """

    id: int | None
    email: str
    name: str
    hashed_password: str
    created_at: datetime
    is_active: bool = True

    def __post_init__(self) -> None:
        """Validacao que roda automaticamente apos o __init__.

        Garante que o email nao esta vazio.
        Este metodo e chamado pelo Python toda vez que criamos um User().
        """
        if not self.email:
            raise ValueError("Email nao pode ser vazio")

        if not self.name:
            raise ValueError("Nome nao pode ser vazio")

    def __repr__(self) -> str:
        """Representacao do objeto para debug.

        IMPORTANTE: Nunca mostramos a senha no __repr__!
        Isso evita que a senha apareca em logs ou prints acidentais.
        """
        return f"User(id={self.id}, email='{self.email}', name='{self.name}')"

    @property
    def is_valid_email(self) -> bool:
        """Verifica se o email contem @ (validacao simples).

        Isso e uma property - chamamos como se fosse um atributo:
            user.is_valid_email  (sem parenteses!)

        Na pratica, usaremos Pydantic para validacao mais robusta.
        Aqui o objetivo e demonstrar o conceito de property.
        """
        return "@" in self.email
