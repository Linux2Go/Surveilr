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
import unittest
from webob import Request

from surveilr.api import server
from surveilr.api.server import application


class APIServerTests(unittest.TestCase):
    def setUp(self):
        import riakalchemy
        riakalchemy.connect()

    def test_create_retrieve_user(self):
        """Create, retrieve, delete, attempt to retrieve again"""
        req = Request.blank('/users',
                            method='POST',
                            POST=json.dumps({}))
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']

        req = Request.blank('/users/%s' % service_id)
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/users/%s' % service_id, method='DELETE')
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/users/%s' % service_id)
        resp = application(req)
        self.assertEquals(resp.status_int, 404)

    def test_send_notification(self):
        req = Request.blank('/users',
                            method='POST',
                            POST=json.dumps({}))
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        user_id = json.loads(resp.body)['id']
        req = Request.blank('/users/%s/notifications' % user_id,
                            method='POST',
                            POST=json.dumps({
                                         'timestamp': 13217362355575,
                                         'metrics': {'duration': 85000,
                                                     'response_size': 12435}}))
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

    def test_create_retrieve_service(self):
        """Create, retrieve, delete, attempt to retrieve again"""
        req = Request.blank('/services',
                            method='POST',
                            POST=json.dumps({'name': 'this_or_the_other'}))
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']

        req = Request.blank('/services/%s' % service_id)
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/services/%s' % service_id, method='DELETE')
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/services/%s' % service_id)
        resp = application(req)
        self.assertEquals(resp.status_int, 404)

    def test_create_retrieve_metric(self):
        req = Request.blank('/services',
                            method='POST',
                            POST='{"name": "this_or_the_other"}')
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        service_id = json.loads(resp.body)['id']
        req = Request.blank('/services/%s/metrics' % service_id,
                            method='POST',
                            POST=json.dumps({
                                         'timestamp': 13217362355575,
                                         'metrics': {'duration': 85000,
                                                     'response_size': 12435}}))
        resp = application(req)
        self.assertEquals(resp.status_int, 200)

        req = Request.blank('/services/%s/metrics' % service_id)
        resp = application(req)

    def test_invalid_url(self):
        req = Request.blank('/stuff')
        resp = application(req)
        self.assertEquals(resp.status_int, 404)

    def test_main(self):
        with mock.patch('surveilr.api.server.eventlet',
                        spec=['listen', 'wsgi']) as eventlet:
            socket_sentinel = mock.sentinel.return_value
            eventlet.listen.return_value = socket_sentinel
            server.main()

            eventlet.listen.assert_called_with(('', 9877))
            eventlet.wsgi.server.assert_called_with(socket_sentinel,
                                                    application)
