"""
Modelos SQLAlchemy do Ebook Creator.

Re-exporta todas as classes para facilitar imports:
    from app.models import Base, User, Project, Chapter, ProjectStatus

IMPORTANTE: Importar todos os modelos aqui garante que o Base.metadata
conheca todas as tabelas. Isso e necessario para:
- Alembic gerar migrations automaticamente
- Base.metadata.create_all() criar todas as tabelas
"""

from app.core.database import Base
from app.models.chapter import Chapter
from app.models.project import Project, ProjectStatus
from app.models.user import User

__all__ = ["Base", "User", "Project", "ProjectStatus", "Chapter"]
