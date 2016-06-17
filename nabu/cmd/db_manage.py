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

from oslo_config import cfg

from nabu.db import migration
from nabu import service


def do_version(conf):
    print('Current DB revision is %s' % migration.version(conf))


def do_upgrade(conf):
    migration.upgrade(conf, conf.command.revision)


def do_stamp(conf):
    migration.stamp(conf, conf.command.revision)


def do_revision(conf):
    migration.revision(conf,
                       message=conf.command.message,
                       autogenerate=conf.command.autogenerate)


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('version')
    parser.set_defaults(func=do_version)

    parser = subparsers.add_parser('upgrade')
    parser.add_argument('revision', nargs='?')
    parser.set_defaults(func=do_upgrade)

    parser = subparsers.add_parser('stamp')
    parser.add_argument('revision')
    parser.set_defaults(func=do_stamp)

    parser = subparsers.add_parser('revision')
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')
    parser.set_defaults(func=do_revision)


def main():
    command_opt = cfg.SubCommandOpt('command',
                                    title='Command',
                                    help='Available commands',
                                    handler=add_command_parsers)
    conf = cfg.ConfigOpts()
    conf.register_cli_opt(command_opt)
    conf = service.prepare_service(conf=conf)

    conf(project='nabu')
    conf.command.func(conf)
