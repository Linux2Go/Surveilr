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

    Tests for admin tool
"""

import mock
import StringIO
import sys

from surveilr import admin
from surveilr import tests
from surveilr.api import client


class AdminToolTests(tests.TestCase):
    def test_main(self):
        saved_commands = admin.commands

        def restore_commands():
            admin.commands = saved_commands

        testcmdclass = mock.Mock()
        testcmd = mock.Mock()
        testcmdclass.return_value = testcmd

        admin.commands = {'Test': testcmdclass}
        self.addCleanup(restore_commands)

        admin.main(['Test', 'arg2', 'arg3'])

        testcmd.init.assert_called_with(['arg2', 'arg3'])
        testcmd.assert_called_with()

    def _define_test_cmd(self):
        class Foo(admin.Command):
            def get_optparser(inner_self):
                optparser = super(Foo, inner_self).get_optparser()
                optparser.add_option('-m', '--mark_succesful',
                                     action='store_true', dest='succesful')
                optparser.add_option('-r', '--reject',
                                     action='store_true', dest='reject')
                return optparser

            def __call__(inner_self):
                if inner_self.options.succesful:
                    self.succesful = True
                if inner_self.options.reject:
                    raise client.UnauthorizedError('blah')

        def cleanup():
            del admin.commands['Foo']

        self.addCleanup(cleanup)
        return Foo

    def test_command_class_registers_in_commands(self):
        Foo = self._define_test_cmd()

        self.assertTrue('Foo' in admin.commands)
        self.assertEquals(admin.commands['Foo'], Foo)

    def test_command_short_option(self):
        self._define_test_cmd()
        self.succesful = False
        admin.main(['Foo', '-m'])
        self.assertTrue(self.succesful)

    def test_command_long_option(self):
        self._define_test_cmd()
        self.succesful = False
        admin.main(['Foo', '--mark_succesful'])
        self.assertTrue(self.succesful)

    def test_get_client_class(self):
        Foo = self._define_test_cmd()

        self.assertEquals(Foo.get_client_class(True),
                          client.SurveilrDirectClient)
        self.assertEquals(Foo.get_client_class(False),
                          client.SurveilrClient)

    def test_get_auth_obj_with_auth(self):
        Foo = self._define_test_cmd()

        class Options(object):
            pass

        options = Options()
        options.user = 'testuser'
        options.api_key = 'testapi_key'

        auth = Foo.get_auth_obj(options)

        self.assertEquals(len(auth), 2)
        self.assertEquals(auth[0], 'testuser')
        self.assertEquals(auth[1], 'testapi_key')

    def test_get_auth_obj_without_auth(self):
        Foo = self._define_test_cmd()

        class Options(object):
            pass

        options = Options()
        options.user = None
        options.api_key = None

        auth = Foo.get_auth_obj(options)

        self.assertIsNone(auth)

    def _replace_stdout_with_stringio(self):
        saved_stdout = sys.stdout

        def reset_stdout():
            sys.stdout = saved_stdout

        sys.stdout = StringIO.StringIO()
        self.addCleanup(reset_stdout)

    def test_unauthorized_error(self):
        self._replace_stdout_with_stringio()
        self._define_test_cmd()

        ret = admin.main(['Foo', '-r'])

        self.assertFalse(ret)
        self.assertEquals(sys.stdout.getvalue(),
                          'Action not permitted\n')

    def test_cmd_list_if_no_command_given(self):
        self._replace_stdout_with_stringio()
        ret = admin.main([])

        self.assertEquals(ret, False)
        stdout = sys.stdout.getvalue()
        self._check_cmd_list(stdout)

    def test_cmd_list_if_invalid_command_given(self):
        self._replace_stdout_with_stringio()
        ret = admin.main(['this is not a valid command'])

        self.assertEquals(ret, False)
        stdout = sys.stdout.getvalue()
        self._check_cmd_list(stdout)

    def _check_cmd_list(self, stdout):
        self.assertEquals(len(stdout.split('\n')) - 1, len(admin.commands))

        expected_commands = set(admin.commands.keys())
        found_commands = set()

        for l in stdout.split('\n')[:-1]:
            self.assertTrue(l.startswith('Usage:'))
            cmd = l.split(' ')[2]
            found_commands.add(cmd)

        self.assertEquals(expected_commands, found_commands)

    def test_CreateUser_admin(self):
        create_user = admin.CreateUser()

        create_user.init(['--admin'])
        create_user.client = mock.Mock()
        create_user()

        create_user.client.new_user.assert_called_with(admin=True)

    def test_CreateUser_non_admin(self):
        create_user = admin.CreateUser()

        create_user.init([])
        create_user.client = mock.Mock()
        create_user()

        create_user.client.new_user.assert_called_with(admin=False)

    def test_CreateService_no_plugins(self):
        create_service = admin.CreateService()

        create_service.init(['servicename'])
        create_service.client = mock.Mock()
        create_service()

        create_service.client.new_service.assert_called_with('servicename',
                                                             None)

    def test_CreateService_with_plugins(self):
        create_service = admin.CreateService()

        plugins = ['http://foo/bar', 'http://baz/wibble']

        args = ['servicename']
        for plugin in plugins:
            args += ['-p', plugin]

        create_service.init(args)
        create_service.client = mock.Mock()
        create_service()

        create_service.client.new_service.assert_called_with('servicename',
                                                             plugins)

    def test_ShowUser(self):
        self._test_Show_or_Delete('show', 'user')

    def test_ShowService(self):
        self._test_Show_or_Delete('show', 'service')

    def test_DeleteUser(self):
        self._test_Show_or_Delete('delete', 'user')

    def test_DeleteService(self):
        self._test_Show_or_Delete('delete', 'service')

    def _test_Show_or_Delete(self, show_or_delete, type_name):
        cmd = getattr(admin, '%s%s' % (show_or_delete.capitalize(),
                                            type_name.capitalize()))()

        cmd.init(['testid'])
        cmd.client = mock.Mock()
        cmd()

        method_prefix = show_or_delete == 'show' and 'get' or 'delete'
        method_name = '%s_%s' % (method_prefix, type_name)
        method = getattr(cmd.client, method_name)
        method.assert_called_with('testid')
