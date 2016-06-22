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


import falcon
import jsonschema
from oslo_serialization import jsonutils
from zaqarclient.queues.v2 import client as zaqarclient

from nabu.db import api
from nabu import exceptions


subscription_schema = {
    "title": "Subscription",
    "description": "A subscription to notifications",
    "type": "object",
    "properties": {
        "source": {
            "description": "The filter for event to subscribe to",
            "type": "string"
        },
        "target": {
            "description":
                "The name of the Zaqar queue to send matching events",
            "type": "string"
        },
        "message_ttl": {
            "description": "The TTL of the messages pushed to the queue",
            "minimum": 0,
            "type": "integer"
        }
    },
    "required": ["source", "target"]
}


class SubscriptionController(object):

    def __init__(self, conf):
        self.conf = conf

    def on_get(self, req, resp, id):
        sub_api = api.SubscriptionAPI(req.context, self.conf)
        try:
            sub = sub_api.get(id)
        except exceptions.NotFound:
            resp.status = falcon.HTTP_404
        else:
            resp.body = jsonutils.dumps(sub)

    def on_delete(self, req, resp, id):
        sub_api = api.SubscriptionAPI(req.context, self.conf)
        sub_api.delete(id)
        resp.status = falcon.HTTP_204


class SubscriptionRootController(object):

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100

    def __init__(self, conf):
        self.conf = conf

    def on_get(self, req, resp):
        marker = req.get_param('marker')
        limit = req.get_param_as_int('limit', min=0, max=self.MAX_LIMIT)
        sub_api = api.SubscriptionAPI(req.context, self.conf)
        if limit is None:
            limit = self.DEFAULT_LIMIT
        data = [sub.items() for sub in sub_api.list(limit, marker)]
        resp.body = jsonutils.dumps({'subscriptions': data})

    def on_post(self, req, resp):
        data = jsonutils.loads(req.stream.read())
        try:
            jsonschema.validate(data, subscription_schema)
        except jsonschema.ValidationError as e:
            resp.status = falcon.HTTP_400
            resp.body = str(e)
            return
        opts = {
            'os_auth_token': req.context.auth_token,
            'os_auth_url': req.context.auth_url,
            'os_project_id': req.context.project_id,
            'os_service_type': 'messaging'
        }
        auth_opts = {'backend': 'keystone', 'options': opts}
        conf = {'auth_opts': auth_opts}

        endpoint = req.env['keystone.token_auth'].get_endpoint(
            None, 'messaging')

        client = zaqarclient.Client(url=endpoint, conf=conf, version=2.0)
        queue = client.queue(data['target'])
        signed_url_data = queue.signed_url(['messages'], methods=['POST'])
        data['signed_url_data'] = jsonutils.dumps(signed_url_data)
        sub_api = api.SubscriptionAPI(req.context, self.conf)
        resp.body = jsonutils.dumps(sub_api.create(data).items())
        resp.status = falcon.HTTP_201
