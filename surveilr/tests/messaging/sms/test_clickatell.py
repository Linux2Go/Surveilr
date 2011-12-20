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

    Tests for Clickatell driver
"""

import mock

from surveilr import tests
from surveilr.messaging.sms import clickatell_driver
from surveilr.tests import utils


class ClickatellDriverTests(tests.TestCase):
    @mock.patch('surveilr.messaging.sms.clickatell_driver.Clickatell')
    def test_instantiate_client(self, clickatell):
        self.driver = clickatell_driver.ClickatellMessaging()

        sendmsg_defaults = {'callback': 1,
                            'req_feat': 8240,
                            'deliv_ack': 1,
                            'msg_type': 'SMS_TEXT'}
        clickatell.assert_called_with('testuser', 'testpassword', 'testapiid',
                                      sendmsg_defaults=sendmsg_defaults)

    def test_send(self):
        driver = clickatell_driver.ClickatellMessaging()
        driver.client = mock.Mock()

        msisdn = '12345678'
        user = utils.get_test_user(messaging_driver='sms',
                                   messaging_address=msisdn)
        info = utils.get_test_notification_info()

        driver.send(user, info)

        driver.client.sendmsg.assert_called_with(recipients=[msisdn],
                                                 sender='testsender',
                                                 text=str(info))
