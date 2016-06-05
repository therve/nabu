# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

from oslotest import base
from oslo_db.sqlalchemy import test_base

from nabu import context
from nabu.db import models


class TestCase(base.BaseTestCase):

    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.context = context.Context('user_name', 'user_id', 'project',
                                       'project_id', 'domain', 'domain_id',
                                       'token', 'http://aut_url/', ['role1'],
                                       {})


class DbTestCase(TestCase, test_base.DbTestCase):
    def generate_schema(self, engine):
        models.Base.metadata.create_all(engine)
