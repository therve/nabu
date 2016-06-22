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
from nabu import exceptions
from nabu.tests import base


class ApiTests(base.DBTestCase):

    def setUp(self):
        super(ApiTests, self).setUp()
        self.sub_api = api.SubscriptionAPI(self.context, self.conf)
        with self.sub_api._writer() as session:
            models.Base.metadata.create_all(session.connection())

    def test_subscription_create(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        self.assertEqual('project_id', sub.project_id)
        self.assertEqual('queue', sub.target)
        self.assertEqual('compute', sub.source)
        self.assertEqual('data', sub.signed_url_data)
        self.assertEqual(60, sub.message_ttl)

    def test_subscription_get(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        other = self.sub_api.get(sub.id)
        self.assertEqual('project_id', other.project_id)
        self.assertEqual('queue', other.target)
        self.assertEqual('compute', other.source)
        self.assertEqual('data', other.signed_url_data)

    def test_subscription_get_wrong_id(self):
        self.assertRaises(exceptions.NotFound, self.sub_api.get, 'unknown')

    def test_subscription_get_wrong_project(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        self.context.project_id = 'other_project'
        self.assertRaises(exceptions.NotFound, self.sub_api.get, sub.id)

    def test_subscription_list(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        other = self.sub_api.create(
            {'source': 'storage', 'target': 'queue',
             'signed_url_data': 'data'})
        result = [s.items() for s in self.sub_api.list(10, None)]
        result.sort()
        expected = [sub.items(), other.items()]
        expected.sort()
        self.assertEqual(expected, result)

    def test_subscription_list_marker(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        other = self.sub_api.create(
            {'source': 'storage', 'target': 'queue',
             'signed_url_data': 'data'})
        result = self.sub_api.list(1, None).one()
        self.assertIn(result.items(), [sub.items(), other.items()])
        following_result = self.sub_api.list(10, result.id).one().items()
        self.assertIn(following_result, [sub.items(), other.items()])
        self.assertNotEqual(following_result, result.items())

    def test_subscription_list_wrong_marker(self):
        self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        self.assertEqual([], self.sub_api.list(10, 'unknown'))

    def test_subscription_delete(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        data = self.sub_api.delete(sub.id)
        self.assertEqual(1, data)
        self.assertRaises(exceptions.NotFound, self.sub_api.get, sub.id)

    def test_subscription_delete_wrong_id(self):
        self.assertEqual(0, self.sub_api.delete('unknown'))

    def test_subscription_delete_wrong_project(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        self.context.project_id = 'other_project'
        self.sub_api.delete(sub.id)
        self.context.project_id = 'project_id'
        other = self.sub_api.get(sub.id)
        self.assertEqual(other.id, sub.id)

    def test_subscription_match(self):
        sub = self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        self.sub_api.create(
            {'source': 'storage', 'target': 'queue',
             'signed_url_data': 'data'})
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

    def test_subscription_match_wrong_project(self):
        self.sub_api.create(
            {'source': 'compute', 'target': 'queue',
             'signed_url_data': 'data'})
        self.assertEqual(
            [],
            self.sub_api.match('other_project', 'compute', 'event_id').all())

    def test_subscription_match_composed(self):
        sub = self.sub_api.create(
            {'source': 'compute.stopped', 'target': 'queue',
             'signed_url_data': 'data'})
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
            {'source': 'compute.stopped.event_id', 'target': 'queue',
             'signed_url_data': 'data'})
        self.assertEqual(
            sub.id,
            self.sub_api.match('project_id', 'compute.stopped',
                               'event_id').one().id)
        self.assertEqual(
            [],
            self.sub_api.match('project_id', 'compute.started',
                               'event_id').all())
