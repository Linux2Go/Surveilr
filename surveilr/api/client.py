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
        return User.new(self, *args, **kwargs)

    def get_user(self, *args, **kwargs):
        return User.get(self, *args, **kwargs)

    def delete_user(self, *args, **kwargs):
        return User.delete(self, *args, **kwargs)

    def new_service(self, *args, **kwargs):
        return Service.new(self, *args, **kwargs)

    def get_service(self, *args, **kwargs):
        return Service.get(self, *args, **kwargs)

    def delete_service(self, *args, **kwargs):
        return Service.delete(self, *args, **kwargs)

    def send_req(self, url_tail, method, body):
        http = httplib2.Http()
        if self.auth:
            http.add_credentials(self.auth[0], self.auth[1])

        url = '%s/%s' % (self.url, url_tail)

        resp, contents = http.request(url, method=method, body=body)
        if resp.status == 403:
            raise UnauthorizedError(resp.reason)
        return contents


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
    keys = []

    def __init__(self, client, **kwargs):
        self.client = client
        for key in self.keys:
            setattr(self, key, kwargs[key])

    @classmethod
    def req(cls, client, action, data, parent=None):
        if action == 'create':
            kwargs = {'method': 'POST', 'body': json.dumps(data)}
            url_tail = '/%ss' % (cls.url_part)
        elif action == 'get':
            kwargs = {'method': 'GET'}
            url_tail = '/%ss/%s' % (cls.url_part, data)
        elif action == 'delete':
            kwargs = {'method': 'DELETE'}
            url_tail = '/%ss/%s' % (cls.url_part, data)

        if parent is not None:
            url_tail = parent.instance_url_tail() + url_tail

        return client.send_req(url_tail, **kwargs)

    def instance_url_tail(self):
        return '/%ss/%s' % (self.url_part, self.id)

    @classmethod
    def delete(cls, client, id):
        return cls.req(client, 'delete', id)

    @classmethod
    def get(cls, client, id):
        return cls.json_deserialise(client, cls.req(client, 'get', id))

    def __repr__(self):
        return ('<%s object%s>' %
                (self.__class__.__name__,
                 ''.join([', %s=%r' %
                         (key, getattr(self, key)) for key in self.keys])))


class User(APIObject):
    url_part = 'user'
    keys = ['id', 'key', 'admin']

    @classmethod
    def json_deserialise(cls, client, s):
        d = json.loads(s)
        return cls(client, id=d.get('id'),
                           key=d.get('key'),
                           admin=d.get('admin', False))

    @classmethod
    def new(cls, client, admin=False):
        return cls.json_deserialise(client,
                                    cls.req(client,
                                            'create',
                                            {'admin': admin}))


class Service(APIObject):
    url_part = 'service'
    keys = ['id', 'name', 'plugins']

    @classmethod
    def json_deserialise(cls, client, s):
        d = json.loads(s)
        return cls(client, id=d.get('id'),
                           name=d.get('name'),
                           plugins=d.get('plugins', []))

    @classmethod
    def new(cls, client, name, plugins=None):
        return cls.json_deserialise(client,
                                    cls.req(client, 'create',
                                            {'name': name,
                                             'plugins': plugins}))

    def new_metric(self, *args, **kwargs):
        return Metric.new(self.client, self, *args, **kwargs)


class Metric(APIObject):
    url_part = 'metric'
    keys = ['id', 'service', 'timestamp', 'metrics']

    @classmethod
    def json_deserialise(cls, client, s):
        d = json.loads(s)
        return cls(client, id=d.get('id'),
                           service=d.get('service'),
                           timestamp=d.get('timestamp'),
                           metrics=d.get('metrics'))

    @classmethod
    def new(cls, client, service, metrics):
        return cls.json_deserialise(client,
                                    cls.req(client, 'create',
                                            {'metrics': metrics},
                                             parent=service))
