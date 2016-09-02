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

from oslo_context import context

from oslo_db.sqlalchemy import enginefacade


@enginefacade.transaction_context_provider
class Context(context.RequestContext):

    def __init__(self, user_name, user_id, project, project_id, domain_name,
                 domain_id, auth_token, auth_url, roles):
        self.project_id = project_id
        self.user_id = user_id
        self.domain_id = domain_id
        self.auth_url = auth_url
        super(Context, self).__init__(
            auth_token=auth_token,
            user=user_name,
            tenant=project,
            user_domain=domain_name,
            roles=roles)


@enginefacade.transaction_context_provider
class DispatcherContext(object):
    """Straightforward context to be used in the dispatcher."""
