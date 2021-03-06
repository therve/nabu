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

from keystoneauth1.identity.generic import password
from keystoneauth1 import session
from zaqarclient.queues.v2 import client as zaqarclient

from nabu import context
from nabu.db import api
from nabu import service


class EventDispatcher(object):
    """Dispatcher class to send event to Zaqar.

    This dispatcher looks up for subscriptions in the Nabu database, and send
    matching events to the configured Zaqar queue.

    To enable this dispatcher, the following section needs to be present in
    ceilometer.conf file

    [DEFAULT]
    event_dispatchers = nabu
    """
    def __init__(self, conf):
        self.context = context.DispatcherContext()
        self.nabu_conf = service.prepare_service([])
        self.api = api.SubscriptionAPI(self.context, self.nabu_conf)
        self._endpoint = None

    @property
    def endpoint(self):
        if self._endpoint is None:
            conf = self.nabu_conf.keystone_authtoken
            auth_plugin = password.Password(
                username=conf.username,
                password=conf.password,
                auth_url=conf.auth_url,
                project_name=conf.project_name)
            sess = session.Session(auth=auth_plugin)
            self._endpoint = sess.get_endpoint(service_type='messaging')
        return self._endpoint

    def record_events(self, events):
        if not isinstance(events, list):
            events = [events]

        for event in events:
            ids = [trait[2] for trait in event['traits']
                   if trait[0] == 'project_id']
            if len(ids) != 1:
                # Nothing we can do with that event
                continue
            project_id = ids[0]
            ids = [trait[2] for trait in event['traits']
                   if trait[0] == 'instance_id']
            instance_id = ids[0] if len(ids) == 1 else None
            subscribers = self.api.match(project_id, event['event_type'],
                                         instance_id)
            for sub in subscribers:
                self._send(sub, event)

    def _send(self, subscriber, event):
        """Send event data to the given subscriber using Zaqar."""
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
        client = zaqarclient.Client(url=self.endpoint, conf=conf, version=2)
        queue = client.queue(subscriber.target, auto_create=False)
        queue.post({'body': event, 'ttl': subscriber.message_ttl})
