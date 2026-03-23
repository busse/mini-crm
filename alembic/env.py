"""Alembic environment configuration.

Configures Alembic to work with our SQLAlchemy models and database.
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models for autogenerate support
# from app.models import Base
# target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    pass


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    pass


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
