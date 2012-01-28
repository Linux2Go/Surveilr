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

    Tests for API server auth
"""

from surveilr import models
from surveilr import tests
from surveilr.api.server import auth


class TestAPIServerAuth(tests.TestCase):
    def test_AlwaysRequireAuth_unauthenticated(self):
        decider = auth.AlwaysRequireAuth()
        self.assertEquals(decider({}, '200 OK', {}), True)

    def test_AlwaysRequireAuth_already_authenticated(self):
        decider = auth.AlwaysRequireAuth()
        self.assertEquals(decider({'repoze.who.identity': 'someone'},
                                  '200 OK', {}), False)


class TestSurveilrAuthPlugin(tests.TestCase):
    def test_authenticate_invcomplete_identity(self):
        env = {}
        identity = {'password': 'apikey'}

        self.assertIsNone(auth.SurveilrAuthPlugin().authenticate(env,
                                                                 identity))
        self.assertEquals(env, {})

    def test_authenticate_invalid_identity(self):
        env = {}
        identity = {'login': 'testuser',
                    'password': 'apikey'}

        self.assertIsNone(auth.SurveilrAuthPlugin().authenticate(env,
                                                                 identity))
        self.assertEquals(env, {})

    def test_authenticate_valid_credentials(self):
        env = {}

        user = models.User()
        user.save()
        identity = {'login': user.key,
                    'password': user.api_key}

        self.assertEquals(auth.SurveilrAuthPlugin().authenticate(env,
                                                                 identity),
                          user.key)
        self.assertEquals(env['surveilr.user'].key, user.key)

    def test_authenticate_wrong_key(self):
        env = {}

        user = models.User()
        user.save()
        self.addCleanup(user.delete)

        identity = {'login': user.key,
                    'password': 'not the right key'}

        self.assertIsNone(auth.SurveilrAuthPlugin().authenticate(env,
                                                                 identity),
                          user.key)
        self.assertEquals(env, {})
