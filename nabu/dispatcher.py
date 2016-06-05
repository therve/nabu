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

from nabu import context
from nabu.db import api


class EventDispatcher(object):

    def __init__(self):
        self.context = context.DispatcherContext()

    def record_events(self, events):
        if not isinstance(events, list):
            events = [events]

        for event in events:
            project_id = event.get('project_id')
            if project_id is None:
                # Nothing we can do with that event
                continue
            subscribers = api.subscription_match(self.context, project_id,
                                                 event['type'], event['id'])
            for sub in subscribers:
                sub.send(event)