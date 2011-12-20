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

    BulkSMS driver
"""
from surveilr import config
from surveilr import drivers

import BulkSMS


class BulkSMSMessaging(object):
    def __init__(self):
        username = config.get_str('sms', 'username')
        password = config.get_str('sms', 'password')
        kwargs = {}
        try:
            kwargs['server'] = config.get_str('sms', 'server')
        except config.NoOptionError:
            pass

        self.client = BulkSMS.Server(username, password, **kwargs)

    def send(self, recipient, info):
        sender = config.get_str('sms', 'sender')
        self.client.send_sms(recipients=[recipient.messaging_address],
                             sender=sender,
                             text=str(info))


drivers.register_driver('sms', 'bulksms', BulkSMSMessaging())
