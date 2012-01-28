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

    Python Client for Surveilr
"""

import httplib2
import json


class UnauthorizedError(Exception):
    pass


class SurveilrClient(object):
    def __init__(self, url, auth=None):
        self.url = url
        self.auth = auth

    def new_user(self, *args, **kwargs):
        user = User.new(self, *args, **kwargs)
        return user

    def send_req(self, url_tail, method, body):
        http = httplib2.Http()
        if self.auth:
            http.add_credentials(self.auth[0], self.auth[1])

        url = '%s/%s' % (self.url, url_tail)

        resp, contents = http.request(url, method=method, body=body)
        if resp.status == 403:
            raise UnauthorizedError(resp.reason)
        return contents

    def req(self, obj_type, action, data):
        if action == 'create':
            method = 'POST'
            url_tail = '/%ss' % (obj_type.url_part)

        return self.send_req(url_tail, method=method, body=json.dumps(data))


class SurveilrDirectClient(SurveilrClient):
    def __init__(self, *args, **kwargs):
        super(SurveilrDirectClient, self).__init__(*args, **kwargs)
        import surveilr.api.server.app
        self.app = surveilr.api.server.app.SurveilrApplication({})

    def send_req(self, url_tail, method, body):
        from webob import Request

        req = Request.blank(url_tail, method=method, body=body)
        req.environ['backdoored'] = True
        resp = self.app(req)
        return resp.body


class APIObject(object):
    def __init__(self, client):
        self.client = client

    def req(self, action, data):
        return self.client.req(type(self), action, data)


class User(APIObject):
    url_part = 'user'

    def __init__(self, client, obj_data=None):
        self.client = client
        obj_data = json.loads(obj_data)
        self.user_id = obj_data['id']
        self.key = obj_data['key']
        self.admin = obj_data['admin']

    @classmethod
    def new(cls, client, admin=False):
        return cls(client, client.req(cls, 'create', {'admin': admin}))

    def __repr__(self):
        return ('<User object, user_id=%r, key=%r, admin=%r>' %
                (self.user_id, self.key, self.admin))
