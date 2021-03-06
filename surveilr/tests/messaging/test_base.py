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

    Tests for messaging layer
"""

import mock

from surveilr import drivers
from surveilr import messaging
from surveilr import tests
from surveilr.tests import utils


class MessagingAPITests(tests.TestCase):
    def test_send(self):
        user = utils.get_test_user()
        info = {'service': 'service_id',
                'state': 'normal',
                'previous_state': 'unexpected high'}

        with mock.patch('surveilr.messaging._get_driver') as _get_driver:
            messaging.send(user, info)

            # Check that _get_driver gets called with the user as its argument
            _get_driver.assert_called_with(user)

            # Check that _get_driver's return value (i.e. the driver)
            # gets its .send() method called with user and info as its
            # arguments
            _get_driver.return_value.send.assert_called_with(user, info)

    def test_get_driver_default(self):
        user = utils.get_test_user()
        expected_driver = drivers.get_driver('messaging', 'fake')

        actual_driver = messaging._get_driver(user)
        self.assertEquals(actual_driver, expected_driver)

    def test_get_driver_sms(self):
        user = utils.get_test_user(messaging_driver='sms')
        expected_driver = drivers.get_driver('messaging', 'sms')

        actual_driver = messaging._get_driver(user)
        self.assertEquals(actual_driver, expected_driver)

    def test_get_driver_fake(self):
        user = utils.get_test_user(messaging_driver='fake')
        expected_driver = drivers.get_driver('messaging', 'fake')

        actual_driver = messaging._get_driver(user)
        self.assertEquals(actual_driver, expected_driver)
