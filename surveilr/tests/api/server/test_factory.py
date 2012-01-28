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

    Tests for API server factory
"""

import mock

from surveilr import tests
from surveilr.api.server import factory


class APIServerFactoryTests(tests.TestCase):
    def test_server_factory_returns_callable(self):
        self.assertTrue(callable(factory.server_factory({}, 'somehost', 1234)))

    @mock.patch('surveilr.api.server.factory.eventlet')
    def test_server_factory_returns_server(self, eventlet):
        testhost = 'somehost'
        testport = '1234'
        serve = factory.server_factory({}, testhost, testport)
        app = mock.sentinel.app

        serve(app)

        eventlet.listen.assert_called_with((testhost, int(testport)))
        eventlet.wsgi.server.assert_called_with(eventlet.listen.return_value,
                                                app)
