#
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

import sys

from oslo_config import cfg
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import session

from nabu.db import models


def get_backend():
    return sys.modules[__name__]


def get_engine():
    facade = session.EngineFacade.from_config(cfg.CONF)
    return facade.get_engine()


@enginefacade.writer
def subscription_create(context, values):
    sub = models.Subscription()
    values['project_id'] = context.project_id
    sub.update(values)
    context.session.add(sub)
    return sub


@enginefacade.reader
def subscription_list(context):
    return context.session.query(models.Subscription).filter_by(
        project_id=context.project_id).all()


@enginefacade.reader
def subscription_get(context, id):
    return context.session.query(models.Subscription).filter_by(
        id=id, project_id=context.project_id).one()


@enginefacade.writer
def subscription_delete(context, id):
    return context.session.query(models.Subscription).filter_by(
        id=id, project_id=context.project_id).delete()
