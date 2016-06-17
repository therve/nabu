# -*- coding: utf-8 -*-

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

import json

import pecan

from zaqarclient.queues.v2 import client as zaqarclient

from nabu.db import api


class SubscriptionController(object):

    def __init__(self, id):
        self.subscription_id = id

    @pecan.expose(generic=True, template='json')
    def index(self, req, resp):
        sub_api = api.SubscriptionAPI(req.context.conf, req.context)
        return sub_api.get(self.subscription_id)

    @index.when(method='DELETE', template='json')
    def index_delete(self, req, resp):
        sub_api = api.SubscriptionAPI(req.context.conf, req.context)
        return sub_api.delete(self.subscription_id)


class SubscriptionRootController(object):

    @pecan.expose()
    def _lookup(self, id, *remainder):
        return SubscriptionController(id), remainder

    @pecan.expose(generic=True, template='json')
    def index(self, req, resp):
        sub_api = api.SubscriptionAPI(req.context.conf, req.context)
        return sub_api.list()

    @index.when(method='POST', template='json')
    def index_post(self, req, resp, **kwargs):
        opts = {
            'os_auth_token': req.context.auth_token,
            'os_auth_url': req.context.auth_url,
            'os_project_id': req.context.project_id,
            'os_service_type': 'messaging'
        }
        auth_opts = {'backend': 'keystone', 'options': opts}
        conf = {'auth_opts': auth_opts}

        endpoint = req.environ['keystone.token_auth'].get_endpoint(
            None, 'messaging')

        client = zaqarclient.Client(url=endpoint, conf=conf, version=2.0)
        data = req.json
        queue = client.queue(data['target'])
        signed_url_data = queue.signed_url(['messages'], methods=['POST'])
        data['signed_url_data'] = json.dumps(signed_url_data)
        sub_api = api.SubscriptionAPI(req.context.conf, req.context)
        return sub_api.create(data)
