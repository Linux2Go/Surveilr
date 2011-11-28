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

    Tests for configuration module
"""

from surveilr import config

import mock
import os.path
import unittest

class ConfigTest(unittest.TestCase):
    def config_files(self):
        return []

    def defaults_file(self):
        return os.path.join(os.path.dirname(__file__),
                            'test_config_defaults.cfg')

    def setUp(self):
        with mock.patch('surveilr.config.defaults_file') as defaults_file:
            with mock.patch('surveilr.config.config_files') as config_files:
                config_files.return_value = self.config_files()
                defaults_file.return_value = self.defaults_file()

                config.load_default_config()

    def tearDown(self):
        config.load_default_config()


class ConfigCoercionTests(ConfigTest):
    def test_str(self):
        get_str = config.get_str
        self.assertEquals(get_str('test_str', 'string'), 'foo')
        self.assertEquals(get_str('test_str', 'multiword'), 'foo bar')
        self.assertEquals(get_str('test_str', 'extra_whitespace'), 'foo  bar')
        self.assertEquals(get_str('test_str', 'num_plus_letters'), '12ab')
        self.assertEquals(get_str('test_str', 'letters_plus_num'), 'ab12')
        self.assertEquals(get_str('test_str', 'numbers'), '12')

    def test_int(self):
        get_int = config.get_int
        self.assertRaises(ValueError, get_int, 'test_int', 'no_numbers')
        self.assertRaises(ValueError, get_int, 'test_int', 'num_plus_letters')
        self.assertRaises(ValueError, get_int, 'test_int', 'letters_plus_num')
        self.assertRaises(ValueError, get_int, 'test_int', 'whitespace')
        self.assertRaises(ValueError, get_int, 'test_int', 'looks_hex')
        self.assertEquals(get_int('test_int', 'numbers'), 12)

    def test_bool(self):
        get_bool = config.get_bool
        self.assertEquals(get_bool('test_bool', 'true'), True)
        self.assertEquals(get_bool('test_bool', 'yes'), True)
        self.assertEquals(get_bool('test_bool', 'one'), True)
        self.assertEquals(get_bool('test_bool', 'on'), True)

        self.assertEquals(get_bool('test_bool', 'false'), False)
        self.assertEquals(get_bool('test_bool', 'no'), False)
        self.assertEquals(get_bool('test_bool', 'zero'), False)
        self.assertEquals(get_bool('test_bool', 'off'), False)

        self.assertRaises(ValueError, get_bool, 'test_bool', 'nonsense')

class ConfigPrecedenceTests(ConfigTest):
    def config_files(self):
        return [os.path.join(os.path.dirname(__file__),
                            'test_config_config.cfg')]

    def test_user_config_overrides_defaults(self):
        self.assertEquals(config.get_str('test_override', 'foo'), 'baz')
