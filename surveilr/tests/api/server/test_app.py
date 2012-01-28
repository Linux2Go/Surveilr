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

    Tests for API server
"""

import json
import mock
from webob import Request

from surveilr import models
from surveilr import tests
from surveilr import utils
from surveilr.api.server import app
from surveilr.api.server.app import SurveilrApplication


class APIServerTests(tests.TestCase):
    def setUp(self):
        super(APIServerTests, self).setUp()
        self.application = SurveilrApplication({})

    def test_create_user_denied(self):
        """Creating a user is refused for non-privileged users"""
        req = Request.blank('/users',
                            method='POST',
                            POST=json.dumps({'messaging_driver': 'fake',
                                             'messaging_address': 'foo'}))

        class FakeUser(object):
            credentials = {'admin': False}

        req.environ['surveilr.user'] = FakeUser()
        resp = self.application(req)
        self.assertEquals(resp.status_int, 403)

    def test_create_retrieve_user(self):
        self._test_create_retrieve_user()

    def test_create_retrieve_admin_user(self):
        self._test_create_retrieve_user(admin=True)

    def _test_create_retrieve_user(self, admin=False):
        """Create, retrieve, delete, attempt to retrieve again (user)"""
        req = Request.blank('/users',
                            method='POST',
                            POST=json.dumps({'messaging_driver': 'fake',
                                             'messaging_address': 'foo',
                                             'admin': True}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']

        req = Request.blank('/users/%s' % service_id)
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        user = json.loads(resp.body)
        self.assertEquals(user['messaging_driver'], 'fake')
        self.assertEquals(user['messaging_address'], 'foo')
        self.assertEquals(user['admin'], True)

        req = Request.blank('/users/%s' % service_id, method='DELETE')
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/users/%s' % service_id)
        resp = self.application(req)
        self.assertEquals(resp.status_int, 404)

    def test_send_notification(self):
        req = Request.blank('/users',
                            method='POST',
                            POST=json.dumps({}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        user_id = json.loads(resp.body)['id']
        req = Request.blank('/users/%s/notifications' % user_id,
                            method='POST',
                            POST=json.dumps({
                                         'timestamp': 13217362355575,
                                         'metrics': {'duration': 85000,
                                                     'response_size': 12435}}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

    def test_create_retrieve_service(self):
        """Create, retrieve, delete, attempt to retrieve again (service)"""
        req = Request.blank('/services',
                            method='POST',
                            POST=json.dumps({'name': 'this_or_the_other'}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']

        req = Request.blank('/services/%s' % service_id)
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/services/%s' % service_id, method='DELETE')
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/services/%s' % service_id)
        resp = self.application(req)
        self.assertEquals(resp.status_int, 404)

    def test_add_remove_plugin_to_service(self):
        url = 'http://foo.bar/'
        req = Request.blank('/services',
                            method='POST',
                            POST=json.dumps({'name': 'this_or_the_other'}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']

        def get_plugins(service_id):
            req = Request.blank('/services/%s' % service_id)
            resp = self.application(req)
            self.assertEquals(resp.status_int, 200)
            print 'body', resp.body
            return json.loads(resp.body)['plugins']

        req = Request.blank('/services/%s' % service_id, method="PUT",
                            POST=json.dumps({'plugins': [url]}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        plugins = get_plugins(service_id)
        self.assertEquals(plugins, [url])

        req = Request.blank('/services/%s' % service_id, method="PUT",
                            POST=json.dumps({'plugins': []}))
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        plugins = get_plugins(service_id)
        self.assertEquals(plugins, [])

    def test_create_retrieve_metric(self):
        req = Request.blank('/services',
                            method='POST',
                            POST='{"name": "this_or_the_other"}')
        resp = self.application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']
        req = Request.blank('/services/%s/metrics' % service_id,
                            method='POST',
                            POST=json.dumps({
                                         'timestamp': 13217362355575,
                                         'metrics': {'duration': 85000,
                                                     'response_size': 12435}}))
        with mock.patch('surveilr.api.server.app.eventlet') as eventlet:
            resp = self.application(req)

            self.assertEquals(eventlet.spawn_n.call_args[0][0],
                              utils.enhance_data_point)
            self.assertEquals(type(eventlet.spawn_n.call_args[0][1]),
                              models.LogEntry)

        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/services/%s/metrics' % service_id)
        resp = self.application(req)

    def test_invalid_url(self):
        req = Request.blank('/stuff')
        resp = self.application(req)
        self.assertEquals(resp.status_int, 404)

    @mock.patch('surveilr.api.server.app.eventlet', spec=['listen', 'wsgi'])
    @mock.patch('surveilr.api.server.app.riakalchemy', spec=['connect'])
    def test_main(self, riakalchemy, eventlet):
        socket_sentinel = mock.sentinel.return_value
        eventlet.listen.return_value = socket_sentinel
        app.main()

        riakalchemy.connect.assert_called_with(host='127.0.0.1', port=8098)
        eventlet.listen.assert_called_with(('', 9877))
        self.assertEquals(eventlet.wsgi.server.call_args[0][0],
                          socket_sentinel)
        self.assertEquals(type(eventlet.wsgi.server.call_args[0][1]),
                          type(self.application))
