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

from oslotest import base

from nabu import context
from nabu import service


class TestCase(base.BaseTestCase):

    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.context = context.Context('user_name', 'user_id', 'project',
                                       'project_id', 'domain', 'domain_id',
                                       'token', 'http://auth_url/', ['role1'])


class DBTestCase(TestCase):

    def setUp(self):
        super(DBTestCase, self).setUp()
        self.conf = service.prepare_service([])
        self.conf.set_override('connection', 'sqlite://', 'database')
