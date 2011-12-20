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

    Tests for BulkSMS driver
"""

import mock

from surveilr import tests
from surveilr.messaging.sms import bulksms_driver
from surveilr.tests import utils


class BulkSMSDriverTests(tests.TestCase):
    @mock.patch('surveilr.messaging.sms.bulksms_driver.BulkSMS')
    def test_instantiate_client(self, BulkSMS):
        self.driver = bulksms_driver.BulkSMSMessaging()
        BulkSMS.Server.assert_called_with('testuser', 'testpassword')

    @mock.patch('surveilr.messaging.sms.bulksms_driver.BulkSMS')
    def test_instantiate_client_override_server(self, BulkSMS):
        self.set_cfg_value('sms', 'server', 'testserver')
        self.driver = bulksms_driver.BulkSMSMessaging()
        BulkSMS.Server.assert_called_with('testuser', 'testpassword',
                                          server='testserver')

    def test_send(self):
        driver = bulksms_driver.BulkSMSMessaging()
        driver.client = mock.Mock()

        msisdn = '12345678'
        user = utils.get_test_user(messaging_driver='sms',
                                   messaging_address=msisdn)
        info = utils.get_test_notification_info()

        driver.send(user, info)

        driver.client.send_sms.assert_called_with(recipients=[msisdn],
                                                  sender='testsender',
                                                  text=str(info))
