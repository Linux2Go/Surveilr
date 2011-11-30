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
"""

import mock
import os.path
import unittest

from surveilr import config


class TestCase(unittest.TestCase):
    def config_files(self):
        module = self.__module__
        if not module.startswith('surveilr.tests'):
            return

        cfg_file = '%s.cfg' % (os.path.join(os.path.dirname(__file__),
                                            *module.split('.')[2:]),)
        return [cfg_file]

    def defaults_file(self):
        return os.path.join(os.path.dirname(__file__),
                            os.path.pardir, 'defaults.cfg')

    def setUp(self):
        super(TestCase, self).setUp()
        with mock.patch('surveilr.config.defaults_file') as defaults_file:
            with mock.patch('surveilr.config.config_files') as config_files:
                config_files.return_value = self.config_files()
                defaults_file.return_value = self.defaults_file()

                config.load_default_config()

    def tearDown(self):
        config.load_default_config()
