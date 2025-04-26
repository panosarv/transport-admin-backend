"""create users and roles tables

Revision ID: 0001_create_users_roles
Revises: 
Create Date: 2025-04-26 
Author: [parvanitis]
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_users_roles'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, nullable=False, unique=True),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id'), nullable=False),
    )
    op.bulk_insert(
        sa.table('roles', sa.column('name', sa.String)),
        [{'name': 'Admin'}, {'name': 'Driver'}]
    )

def downgrade():
    op.drop_table('users')
    op.drop_table('roles')
