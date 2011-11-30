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

import surveilr.messaging.fake
import surveilr.messaging.sms

from surveilr import drivers


def _get_driver(recipient):
    return drivers.get_driver('messaging',
                              getattr(recipient, 'messaging_driver', 'fake'))


def send(recipient, info):
    driver = _get_driver(recipient)
    driver.send(recipient, info)
