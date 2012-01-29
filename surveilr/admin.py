#!/usr/bin/env python
"""
    Surveilr - Log aggregation, analysis and visualisation

    Copyright (C) 2011  Linux2Go

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU Affero General Public License
    as published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public
    License along with this program.  If not, see
    <http://www.gnu.org/licenses/>.

    Admin tool
"""

import optparse
import sys

import surveilr.api.client

commands = {}


class CommandMeta(type):
    def __new__(mcs, name, bases, dict):
        cls = type.__new__(mcs, name, bases, dict)
        if not (len(bases) == 1 and object in bases):
            commands[name] = cls
        return cls


class Command(object):
    __metaclass__ = CommandMeta

    def get_optparser(self):
        optparser = optparse.OptionParser(usage='%%prog %s [options]' %
                                                 self.__class__.__name__)
        optparser.add_option('--direct', action='store_true', default=False,
                             help='Talk directly to Surveilr WSGI app')
        optparser.add_option('--url', action='store',
                             default='http://localhost:8977/surveilr')
        optparser.add_option('--user', action='store', help='User id')
        optparser.add_option('--api_key', action='store', help='API key')
        return optparser

    def __init__(self):
        self.optparser = self.get_optparser()

    @classmethod
    def get_client_class(self, direct):
        if direct:
            return surveilr.api.client.SurveilrDirectClient
        else:
            return surveilr.api.client.SurveilrClient

    @classmethod
    def get_auth_obj(cls, options):
        if options.user and options.api_key:
            return (options.user, options.api_key)
        else:
            return None

    def init(self, argv=None):
        if argv is None:  # pragma: nocover
            argv = sys.argv

        self.options, self.args = self.optparser.parse_args(argv)
        client_class = self.get_client_class(self.options.direct)
        auth = self.get_auth_obj(self.options)

        self.client = client_class(self.options.url, auth)


class CreateUser(Command):
    def get_optparser(self):
        optparser = super(CreateUser, self).get_optparser()
        optparser.add_option('--admin', action='store_true', default=False,
                             help='Make the new user an admin')
        return optparser

    def __call__(self):
        user = self.client.new_user(admin=self.options.admin)

        print 'User created.'
        print 'ID:', user.user_id
        print 'API key:', user.key
        print 'Admin:', user.admin
        print '--user %s --api_key %s' % (user.user_id, user.key)


class ShowUser(Command):
    def __call__(self):
        user = self.client.get_user(self.args[0])

        print 'User:'
        print 'ID:', user.user_id
        print 'Admin:', user.admin


class DeleteUser(Command):
    def __call__(self):
        self.client.delete_user(self.args[0])
        print 'User deleted'


class ShowService(Command):
    def __call__(self):
        service = self.client.get_service(self.args[0])

        print 'Service:'
        print 'ID:', service.id
        print 'Name:', service.name
        print 'Plugins:', service.plugins


class DeleteService(Command):
    def __call__(self):
        self.client.delete_service(self.args[0])
        print 'Service deleted'


class CreateService(Command):
    def get_optparser(self):
        optparser = super(CreateService, self).get_optparser()
        optparser.add_option('-p', action='append', dest='plugins',
                             help='Make the new user an admin')
        return optparser

    def __call__(self):
        service = self.client.new_service(self.args[0],
                                          self.options.plugins)
        print 'Service:'
        print 'ID:', service.id


def usage():
    for cmd_name in commands:
        cmd = commands[cmd_name]()
        print cmd.optparser.get_usage().strip()


def main(argv=None):
    if argv is None:  # pragma: nocover
        argv = sys.argv[1:]

    if not len(argv):
        usage()
        return False

    if argv[0] in commands:
        try:
            cmd = commands[argv[0]]()
            cmd.init(argv[1:])
            return cmd()
        except surveilr.api.client.UnauthorizedError:
            print 'Action not permitted'
            return False
    else:
        usage()
        return False


if __name__ == '__main__':  # pragma: nocover
    sys.exit(not main())
