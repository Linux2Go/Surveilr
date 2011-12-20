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

    Clickatell SMS driver
"""
from surveilr import config
from surveilr import drivers

from clickatell.api import Clickatell
from clickatell import constants as cc


class ClickatellMessaging(object):
    def __init__(self):
        username = config.get_str('sms', 'username')
        password = config.get_str('sms', 'password')
        api_id = config.get_str('sms', 'api_id')
        self.client = Clickatell(username, password, api_id,
                                 sendmsg_defaults={
                                    'callback': cc.YES,
                                    'msg_type': cc.SMS_DEFAULT,
                                    'deliv_ack': cc.YES,
                                    'req_feat': (cc.FEAT_ALPHA +
                                                 cc.FEAT_NUMER +
                                                 cc.FEAT_DELIVACK)
                              })

    def send(self, recipient, info):
        sender = config.get_str('sms', 'sender')
        self.client.sendmsg(recipients=[recipient.messaging_address],
                            sender=sender,
                            text=str(info))


drivers.register_driver('sms', 'clickatell', ClickatellMessaging())
