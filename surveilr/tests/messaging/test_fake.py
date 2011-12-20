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

    Tests for fake messaging driver
"""

from surveilr import drivers
from surveilr import tests
from surveilr.tests import utils


class FakeMessagingDriverTests(tests.TestCase):
    def setUp(self):
        import surveilr.messaging.fake
        # This does nothing, but pyflakes gets upset if we import it
        # and never "use" it.
        surveilr.messaging.fake
        self.driver = drivers.get_driver('messaging', 'fake')

    def test_send(self):
        user = utils.get_test_user()
        info = {'service': 'service_id',
                'state': 'normal',
                'previous_state': 'unexpected high'}
        self.driver.send(user, info)
