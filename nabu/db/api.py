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

from sqlalchemy.orm import exc

from oslo_db.sqlalchemy import enginefacade

from nabu.db import models
from nabu import exceptions


class SubscriptionAPI(object):

    def __init__(self, context):
        self._transaction = enginefacade.transaction_context()
        self._transaction.configure(
            **dict(context.conf.database.items())
        )
        self._context = context

    def _reader(self):
        return self._transaction.reader.using(self._context)

    def _writer(self):
        return self._transaction.writer.using(self._context)

    def create(self, values):
        with self._writer() as session:
            sub = models.Subscription()
            values['project_id'] = self._context.project_id
            sub.update(values)
            session.add(sub)
            return sub

    def list(self):
        with self._reader() as session:
            return session.query(models.Subscription).filter_by(
                project_id=self._context.project_id).all()

    def get(self, id):
        try:
            with self._reader() as session:
                return session.query(models.Subscription).filter_by(
                    id=id, project_id=self._context.project_id).one()
        except exc.NoResultFound:
            raise exceptions.NotFound()

    def delete(self, id):
        with self._writer() as session:
            return session.query(models.Subscription).filter_by(
                id=id, project_id=self._context.project_id).delete()

    def match(self, project_id, event_type, event_id):
        fragments = event_type.split('.')
        if event_id:
            fragments.append(event_id)
        fragment_filter = []
        for index in range(len(fragments)):
            fragment_filter.append('.'.join(fragments[:index + 1]))
        with self._reader() as session:
            query = session.query(models.Subscription).filter_by(
                project_id=project_id)
            return query.filter(
                models.Subscription.source.in_(fragment_filter))
