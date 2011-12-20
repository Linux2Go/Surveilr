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

    Tests for driver infrastructure
"""

from surveilr import drivers
from surveilr import exceptions
from surveilr import tests


class DriversTests(tests.TestCase):
    def register_empty_driver(self, driver_type, driver_name,
                              add_cleanup=True):
        class SomeDriver(object):
            pass

        driver = SomeDriver()
        drivers.register_driver(driver_type, driver_name, driver)
        if add_cleanup:
            self.addCleanup(drivers.unregister_driver,
                            driver_type, driver_name)
        return driver

    def test_register_retrieve_driver(self):
        """Register driver and retrieve it again"""
        driver = self.register_empty_driver('some_type', 'some_name')
        self.assertTrue(drivers.get_driver('some_type', 'some_name') is driver)

    def test_register_duplicate_driver(self):
        """Registering duplicate driver fails"""
        self.register_empty_driver('some_type', 'some_name')
        self.assertRaises(exceptions.DuplicateDriverError,
                          self.register_empty_driver,
                          'some_type',
                          'some_name')

    def test_get_invalid_driver_type(self):
        """Retrieve driver of unknown type fails"""
        self.assertRaises(exceptions.UnknownDriverTypeError,
                          drivers.get_driver,
                          'unknown_type',
                          'some_name')

    def test_get_invalid_driver(self):
        """Retrieve unknown driver of known type fails"""
        self.register_empty_driver('some_type', 'some_name')
        self.assertRaises(exceptions.UnknownDriverError,
                          drivers.get_driver,
                          'some_type',
                          'unknown_name')

    def test_unregister_unknown_driver_type(self):
        """Unregister driver of unknown type fails"""
        self.assertRaises(exceptions.UnknownDriverTypeError,
                          drivers.unregister_driver,
                          'unknown_type',
                          'some_name')

    def test_unregister_unknown_driver(self):
        """Unregister unknown driver of known type fails"""
        self.register_empty_driver('some_type', 'some_name')
        self.assertRaises(exceptions.UnknownDriverError,
                          drivers.unregister_driver,
                          'some_type',
                          'unknown_name')

    def test_unregister_then_retrieve(self):
        """When last driver of a type is removed, so it the type"""
        self.register_empty_driver('some_type', 'some_name', add_cleanup=False)
        drivers.unregister_driver('some_type', 'some_name')
        self.assertRaises(exceptions.UnknownDriverTypeError,
                          drivers.unregister_driver,
                          'some_type',
                          'some_name')
