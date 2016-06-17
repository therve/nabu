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

from nabu.db import api
from nabu.db import models
from nabu.tests import base


class ApiTests(base.DBTestCase):

    def setUp(self):
        super(ApiTests, self).setUp()
        self.sub_api = api.SubscriptionAPI(self.conf, self.context)
        with self.sub_api._writer() as session:
            models.Base.metadata.create_all(session.connection())

    def test_subscription_match(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'project_id': 'project_id', 'signed_url_data': 'data'})
        self.sub_api.create(
            {'source': 'storage', 'target': 'queue',
             'project_id': 'project_id', 'signed_url_data': 'data'})
        self.assertEqual(
            sub.id,
            self.sub_api.match('project_id', 'compute', 'event_id').one().id)
        self.assertEqual(
            sub.id,
            self.sub_api.match('project_id', 'compute.started',
                               'event_id').one().id)
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'network.stopped',
                               'event_id').all())
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'network.stopped',
                               'event_id').all())
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'network.stopped',
                               'event_id').all())

    def test_subscription_match_composed(self):
        sub = self.sub_api.create(
            {'source': 'compute.stopped', 'target': 'queue',
             'project_id': 'project_id', 'signed_url_data': 'data'})
        self.assertEqual(
            sub.id,
            self.sub_api.match('project_id', 'compute.stopped',
                               'event_id').one().id)
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'network.stopped',
                               'event_id').all())
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'network.stopped',
                               'event_id').all())

    def test_subscription_match_event_id(self):
        sub = self.sub_api.create(
            {'source': 'compute.stopped.event_id',
             'target': 'queue', 'project_id': 'project_id',
             'signed_url_data': 'data'})
        self.assertEqual(
            sub.id,
            self.sub_api.match('project_id', 'compute.stopped',
                               'event_id').one().id)
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'compute.started',
                               'event_id').all())
