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

    Configuration infrastructure
"""

import ConfigParser
import os.path

cfg = None

NoSectionError = ConfigParser.NoSectionError
NoOptionError = ConfigParser.NoOptionError


def defaults_file():
    return os.path.join(os.path.dirname(__file__), 'defaults.cfg')


def config_files():
    return ['/etc/surveilr/surveilr.cfg']


def load_default_config():
    global cfg
    cfg = ConfigParser.SafeConfigParser()
    cfg.readfp(open(defaults_file(), 'r'))
    cfg.read(config_files())


def get_str(section, option):
    return cfg.get(section, option)


def get_int(section, option):
    return cfg.getint(section, option)


def get_bool(section, option):
    return cfg.getboolean(section, option)


load_default_config()
