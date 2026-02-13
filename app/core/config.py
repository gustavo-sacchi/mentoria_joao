"""
Configuracoes da aplicacao usando Pydantic Settings.

Pydantic Settings le variaveis de ambiente automaticamente.
Isso permite ter configuracoes diferentes para dev, teste e producao
sem mudar o codigo - apenas mudando as variaveis de ambiente.

Conceitos ensinados:
- BaseSettings do pydantic-settings
- Leitura automatica de variaveis de ambiente
- Arquivo .env para configuracoes locais
- Instancia global de configuracao (Singleton pattern)
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes centrais da aplicacao.

    O Pydantic Settings procura variaveis de ambiente com o mesmo nome
    dos atributos. Por exemplo, se existir DATABASE_URL no ambiente,
    ele sera usado automaticamente.

    Ordem de prioridade:
    1. Variavel de ambiente (maior prioridade)
    2. Arquivo .env
    3. Valor padrao definido aqui (menor prioridade)
    """

    # --- Banco de Dados ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ebook_creator"

    # --- Autenticacao JWT ---
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuracao do Pydantic Settings:
    # - env_file: le variaveis de um arquivo .env na raiz do projeto
    # - extra="ignore": ignora variaveis extras no .env sem dar erro
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# Instancia global - importamos esta variavel em todo o projeto.
# Isso e semelhante ao pattern Singleton: uma unica fonte de configuracao.
settings = Settings()
