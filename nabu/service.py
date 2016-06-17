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

import sys

from keystoneauth1 import loading
from oslo_config import cfg
from oslo_db import options as db_options
import oslo_i18n
from oslo_log import log

import nabu

OPTS = [
    cfg.StrOpt('api_paste_config',
               default='api_paste.ini',
               help='Configuration file for WSGI definition of API.'
               ),
]


def prepare_service(argv=None, config_files=None, conf=None):
    oslo_i18n.enable_lazy()

    if argv is None:
        argv = sys.argv
    if conf is None:
        conf = cfg.ConfigOpts()
    conf.register_opts(OPTS)
    log.register_options(conf)
    db_options.set_defaults(conf)
    loading.register_auth_conf_options(conf, 'keystone_authtoken')
    conf(argv[1:], project='nabu', validate_default_values=True,
         version=nabu.__version__,
         default_config_files=config_files)
    loading.load_auth_from_conf_options(conf, 'keystone_authtoken')

    log.setup(conf, 'nabu')

    return conf
