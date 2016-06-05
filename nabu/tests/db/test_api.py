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
from nabu.tests import base


class ApiTests(base.DbTestCase):

    def test_subscription_match(self):
        sub = api.subscription_create(
            self.context, {'source': 'compute', 'target': 'queue',
                           'project_id': 'project_id', 'signed_url_data':
                           'data'})
        other_sub = api.subscription_create(
            self.context, {'source': 'storage', 'target': 'queue',
                           'project_id': 'project_id', 'signed_url_data':
                           'data'})
        self.assertEqual(
            sub.id,
            api.subscription_match(self.context, 'project_id', 'compute',
                                   'event_id').one().id)
        self.assertEqual(
            sub.id,
            api.subscription_match(self.context, 'project_id', 'compute.started',
                                   'event_id').one().id)
        self.assertEqual(
            [],
            api.subscription_match(self.context, 'project_id',
                                   'network.stopped', 'event_id').all())
        self.assertEqual(
            [],
            api.subscription_match(self.context, 'project_id',
                                   'network.stopped', 'event_id').all())
        self.assertEqual(
            [],
            api.subscription_match(self.context, 'project_id',
                                   'network.stopped', 'event_id').all())

    def test_subscription_match_composed(self):
        sub = api.subscription_create(
            self.context, {'source': 'compute.stopped', 'target': 'queue',
                           'project_id': 'project_id', 'signed_url_data':
                           'data'})
        self.assertEqual(
            sub.id,
            api.subscription_match(self.context, 'project_id',
                                   'compute.stopped', 'event_id').one().id)
        self.assertEqual(
            [],
            api.subscription_match(self.context, 'project_id',
                                   'network.stopped', 'event_id').all())
        self.assertEqual(
            [],
            api.subscription_match(self.context, 'project_id',
                                   'network.stopped', 'event_id').all())

    def test_subscription_match_event_id(self):
        sub = api.subscription_create(
            self.context, {'source': 'compute.stopped.event_id',
                           'target': 'queue', 'project_id': 'project_id',
                           'signed_url_data': 'data'})
        self.assertEqual(
            sub.id,
            api.subscription_match(self.context, 'project_id',
                                   'compute.stopped', 'event_id').one().id)
        self.assertEqual(
            [],
            api.subscription_match(self.context, 'project_id',
                                   'compute.started', 'event_id').all())
