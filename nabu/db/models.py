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

import uuid

import sqlalchemy
from sqlalchemy.ext import declarative

from oslo_db.sqlalchemy import models


class NabuBase(models.ModelBase, models.TimestampMixin):
    metadata = None


Base = declarative.declarative_base(cls=NabuBase)


class Subscription(Base):
    __tablename__ = 'subscription'

    id = sqlalchemy.Column(sqlalchemy.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    source = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    target = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    project_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    message_ttl = sqlalchemy.Column(sqlalchemy.Integer, default=60,
                                    nullable=False)
    signed_url_data = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
