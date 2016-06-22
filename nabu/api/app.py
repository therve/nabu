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

import os

import falcon
from paste import deploy

from oslo_config import cfg
from oslo_log import log

from nabu._i18n import _LI
from nabu.api.controllers import subscription
from nabu import context
from nabu import service


LOG = log.getLogger(__name__)


class ContextMiddleware(object):

    def __init__(self, conf):
        self.conf = conf

    def process_resource(self, request, response, resource, params):
        headers = request.headers
        user_name = headers.get('X-USER-NAME')
        user_id = headers.get('X-USER-ID')
        project = headers.get('X-PROJECT-NAME')
        project_id = headers.get('X-PROJECT-ID')
        domain_id = headers.get('X-USER-DOMAIN-ID')
        domain_name = headers.get('X-USER-DOMAIN-NAME')
        auth_token = headers.get('X-AUTH-TOKEN')
        auth_url = headers.get('X-AUTH-URL')
        if not auth_url:
            auth_url = self.conf.keystone_authtoken.auth_url
        roles = headers.get('X-ROLES', '').split(',')
        auth_token_info = request.env.get('keystone.token_info')

        request.context = context.Context(
            user_name=user_name,
            user_id=user_id,
            project=project,
            project_id=project_id,
            domain_name=domain_name,
            domain_id=domain_id,
            auth_token=auth_token,
            auth_url=auth_url,
            roles=roles,
            auth_token_info=auth_token_info,
            conf=self.conf)


def setup_app(conf):
    app = falcon.API(middleware=[ContextMiddleware(conf)])
    app.add_route('/v1/subscription',
                  subscription.SubscriptionRootController())
    app.add_route('/v1/subscription/{id}',
                  subscription.SubscriptionController())
    return app


def app_factory(global_config, **local_conf):
    return setup_app(global_config['nabu_config'])


def load_app(conf):
    cfg_file = None
    cfg_path = conf.api_paste_config
    if not os.path.isabs(cfg_path):
        cfg_file = conf.find_file(cfg_path)
    elif os.path.exists(cfg_path):
        cfg_file = cfg_path

    if not cfg_file:
        raise cfg.ConfigFilesNotFoundError([conf.api_paste_config])
    LOG.info(_LI('Full WSGI config used: %s') % cfg_file)
    return deploy.loadapp('config:' + cfg_file,
                          global_conf={'nabu_config': conf})


def init_application():
    conf = service.prepare_service()
    return load_app(conf)
