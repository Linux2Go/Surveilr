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
        return '<User object, user_id=%r, key=%r, admin=%r>' % (self.user_id, self.key, self.admin)
