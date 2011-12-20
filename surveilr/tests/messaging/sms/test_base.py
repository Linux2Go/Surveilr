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

from surveilr import tests
from surveilr.messaging import sms


class SMSMessagingTest(tests.TestCase):
    @mock.patch('surveilr.messaging.sms.drivers')
    def test_init(self, drivers):
        sms.SMSMessaging()
        drivers.get_driver.assert_called_with('sms',
                                              'not_your_average_sms_driver')

    @mock.patch('surveilr.messaging.sms.drivers')
    def test_send(self, drivers):
        drv = sms.SMSMessaging()
        recipient = mock.sentinel.recipient
        info = mock.sentinel.info

        drv.send(recipient, info)

        drivers.get_driver.return_value.send.assert_called_with(recipient,
                                                                info)
