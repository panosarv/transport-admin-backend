import os
import sys
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
from app.models.vehicle import Vehicle
from app.models.role import Role
from app.models.user import User  
from app.models.company import Company  
from app.models.booking import Booking
sys.path.append(os.getcwd())

from app.db.base import Base
from app.core.config import settings

# this is the Alembic Config object
config = context.config

# set up logging (expects [handlers], [formatters], etc. in alembic.ini)
if config.config_file_name:
    fileConfig(config.config_file_name)

# Pull in the DATABASE_URL as a string
db_url = str(settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", db_url)

# our metadata to target
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        future=True,
    )

    async def do_run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(do_run())

def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
