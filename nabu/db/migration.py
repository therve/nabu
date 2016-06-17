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

from alembic import context
from oslo_db.sqlalchemy.migration_cli import manager


def get_manager(conf):
    alembic_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'alembic.ini'))
    migrate_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'alembic'))
    migration_config = {'alembic_ini_path': alembic_path,
                        'alembic_repo_path': migrate_path,
                        'db_url': conf.database.connection}
    mgr = manager.MigrationManager(migration_config)

    context.nabu_config = conf
    return mgr


def version(conf):
    """Current database version.

    :returns: Database version
    :rtype: string
    """
    return get_manager(conf).version()


def upgrade(conf, version):
    """Used for upgrading database.

    :param version: Desired database version
    :type version: string
    """
    version = version or 'head'

    get_manager(conf).upgrade(version)


def stamp(conf, revision):
    """Stamps database with provided revision.

    Don't run any migrations.

    :param revision: Should match one from repository or head - to stamp
                     database with most recent revision
    :type revision: string
    """
    get_manager(conf).stamp(revision)


def revision(conf, message=None, autogenerate=False):
    """Creates template for migration.

    :param message: Text that will be used for migration title
    :type message: string
    :param autogenerate: If True - generates diff based on current database
                         state
    :type autogenerate: bool
    """
    return get_manager(conf).revision(message=message,
                                      autogenerate=autogenerate)
