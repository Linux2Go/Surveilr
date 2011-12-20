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

from surveilr import config
from surveilr import drivers

import surveilr.messaging.sms.fake
import surveilr.messaging.sms.clickatell_driver
import surveilr.messaging.sms.bulksms_driver

class SMSMessaging(object):
    def __init__(self):
        driver_name = config.get_str('sms', 'driver')
        self.driver = drivers.get_driver('sms', driver_name)

    def send(self, recipient, info):
        return self.driver.send(recipient, info)

drivers.register_driver('messaging', 'sms', SMSMessaging())
