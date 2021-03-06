# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Initial migration

Revision ID: a12d1154ace8
Revises: None
Create Date: 2016-06-17 16:47:29.822508

"""

# revision identifiers, used by Alembic.
revision = 'a12d1154ace8'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'subscription',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('target', sa.String(length=255), nullable=False),
        sa.Column('project_id', sa.String(length=255), nullable=False),
        sa.Column('message_ttl', sa.Integer(), nullable=False),
        sa.Column('signed_url_data', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
