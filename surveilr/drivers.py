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

    Driver infrastructure
"""

from surveilr import exceptions

registry = {}


def register_driver(driver_type, name, driver):
    if driver_type not in registry:
        registry[driver_type] = {}

    if name in registry[driver_type]:
        raise exceptions.DuplicateDriverError()

    registry[driver_type][name] = driver


def unregister_driver(driver_type, name):
    if driver_type not in registry:
        raise exceptions.UnknownDriverTypeError()

    if name not in registry[driver_type]:
        raise exceptions.UnknownDriverError()

    del registry[driver_type][name]

    if not registry[driver_type]:
        del registry[driver_type]


def get_driver(driver_type, name):
    if driver_type not in registry:
        raise exceptions.UnknownDriverTypeError()

    if name not in registry[driver_type]:
        raise exceptions.UnknownDriverError()

    return registry[driver_type][name]
