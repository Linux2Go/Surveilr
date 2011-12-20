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
from surveilr.messaging.sms import fake

class FakeSMSMessagingTest(tests.TestCase):
    def test_send(self):
        recipient1 = mock.sentinel.recipient1
        info1 = mock.sentinel.info1
        recipient2 = mock.sentinel.recipient2
        info2 = mock.sentinel.info2

        drv = fake.FakeMessaging()
        drv.send(recipient1, info1)
        drv.send(recipient2, info2)

        self.assertEquals(drv.msgs, [(recipient1, info1),
                                     (recipient2, info2)])
        
