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

import os

from paste import deploy
import pecan

from oslo_config import cfg
from oslo_log import log

from nabu._i18n import _LI
from nabu import context


LOG = log.getLogger(__name__)


OPTS = [
    cfg.StrOpt('api_paste_config',
               default='api_paste.ini',
               help='Configuration file for WSGI definition of API.'
               ),
]

cfg.CONF.register_opts(OPTS)


class ContextHook(pecan.hooks.PecanHook):

    def before(self, state):
        headers = state.request.headers
        user_name = headers.get('X-User-Name')
        user_id = headers.get('X-User-Id')
        project = headers.get('X-Project-Name')
        project_id = headers.get('X-Project-Id')
        domain_id = headers.get('X-User-Domain-Id')
        domain_name = headers.get('X-User-Domain-Name')
        auth_token = headers.get('X-Auth-Token')
        auth_url = headers.get('X-Auth-URL')
        if not auth_url:
            auth_url = cfg.CONF.keystone_authtoken.auth_url
        roles = headers.get('X-Roles', '').split(',')
        auth_token_info = state.request.environ.get('keystone.token_info')

        state.request.context = context.Context(
            user_name=user_name,
            user_id=user_id,
            project=project,
            project_id=project_id,
            domain_name=domain_name,
            domain_id=domain_id,
            auth_token=auth_token,
            auth_url=auth_url,
            roles=roles,
            auth_token_info=auth_token_info)


def setup_app():

    app = pecan.make_app(
        'nabu.api.controllers.root.RootController',
        use_context_locals=False,
        guess_content_type_from_ext=False,
        hooks=[ContextHook()])
    return app


def app_factory(global_config, **local_conf):
    return setup_app()


def load_app():
    # Build the WSGI app
    cfg_file = None
    cfg_path = cfg.CONF.api_paste_config
    if not os.path.isabs(cfg_path):
        cfg_file = cfg.CONF.find_file(cfg_path)
    elif os.path.exists(cfg_path):
        cfg_file = cfg_path

    if not cfg_file:
        raise cfg.ConfigFilesNotFoundError([cfg.CONF.api_paste_config])
    LOG.info(_LI('Full WSGI config used: %s') % cfg_file)
    return deploy.loadapp('config:' + cfg_file)


def init_application():
    from nabu import service
    service.prepare_service()
    return load_app()
