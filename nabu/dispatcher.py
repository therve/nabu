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

from nabu import context
from nabu.db import api
from nabu import service

from ceilometer import dispatcher
from zaqarclient.queues.v2 import client as zaqarclient


class EventDispatcher(dispatcher.EventDispatcherBase):

    def __init__(self, conf):
        self.context = context.DispatcherContext()
        self.context.conf = service.prepare_service([])
        self.api = api.SubscriptionAPI(self.context)
        self.conf = conf

    def record_events(self, events):
        if not isinstance(events, list):
            events = [events]

        for event in events:
            ids = [trait[2] for trait in event['traits']
                   if trait[0] == 'project_id']
            if not ids:
                # Nothing we can do with that event
                continue
            project_id = ids[0]
            ids = [trait[2] for trait in event['traits']
                   if trait[0] == 'instance_id']
            instance_id = ids[0] if ids else None
            subscribers = self.api.match(project_id, event['event_type'],
                                         instance_id)
            for sub in subscribers:
                self._send(sub, event)

    def _send(self, subscriber, event):
        data = json.loads(subscriber.signed_url_data)
        opts = {
            'paths': data['paths'],
            'expires': data['expires'],
            'methods': data['methods'],
            'signature': data['signature'],
            'os_project_id': data['project'],
        }
        auth_opts = {'backend': 'signed-url',
                     'options': opts}
        conf = {'auth_opts': auth_opts}
        endpoint = XXX
        client = zaqarclient.Client(url=endpoint, conf=conf, version=2)
        queue = client.queue(subscriber.target, auto_create=False)
        queue.post({'body': event, 'ttl': subscriber.message_ttl})
