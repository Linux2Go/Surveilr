import json
import mock

from surveilr import tests
from surveilr.api import client

class APIClientTests(tests.TestCase):
    test_url = 'http://somewhere:1234/else'
    test_auth = ('foo', 'bar')

    def _get_client(self, url=None, auth=None):
        if not url:
            url = self.test_url
        if not auth:
            auth = self.test_auth
        return client.SurveilrClient(self.test_url, self.test_auth)


    @mock.patch('surveilr.api.client.User')
    def test_new_user(self, User):
        test_args = ('foo', 'bar', 'baz')
        test_kwargs = {'foo': 'bar',
                       'baz': 'wibble'}

        api_client = self._get_client()
        user = api_client.new_user(*test_args, **test_kwargs)
        User.new.assert_called_with(api_client, *test_args, **test_kwargs)
        self.assertEquals(user, User.new.return_value)


    @mock.patch('surveilr.api.client.httplib2')
    def test_send_req(self, httplib2):
        api_client = self._get_client()

        class FakeResponse(object):
            def __init__(self, status_code):
                self.status = status_code

        http = httplib2.Http.return_value
        http.request.return_value = (FakeResponse(200), 'resp')
        client_response = api_client.send_req('tail', 'METHOD', 'body')
        http.add_credentials.assert_called_with(*self.test_auth)
        http.request.assert_called_with(self.test_url + '/tail',
                                        method='METHOD',
                                        body='body')

        self.assertEquals(client_response, 'resp')


    @mock.patch('surveilr.api.client.httplib2')
    def test_send_req_403_reraises_unauthorized_error(self, httplib2):
        api_client = self._get_client()

        class FakeResponse(object):
            reason = 'Just because, ok?'
            def __init__(self, status_code):
                self.status = status_code

        http = httplib2.Http.return_value
        http.request.return_value = (FakeResponse(403), 'resp')
        self.assertRaises(client.UnauthorizedError,
                          api_client.send_req, 'tail', 'METHOD', 'body')

    def test_req(self):
        api_client = self._get_client()

        test_data = {'foo': ['bar', 'baz', 2]}

        class FakeObjType(object):
            url_part = 'stuff'

        with mock.patch_object(api_client, 'send_req') as send_req:
            api_client.req(FakeObjType(), 'create', test_data)
            self.assertEquals(send_req.call_args[0][0], '/stuffs')
            self.assertEquals(send_req.call_args[1]['method'], 'POST')
            self.assertEquals(json.loads(send_req.call_args[1]['body']),
                              test_data)

    def test_apiobject(self):
        client_obj = mock.Mock()
        data = mock.Sentinel()

        class TestObject(client.APIObject):
            pass

        obj = TestObject(client_obj)
        obj.req('ACTION', data)

        client_obj.req.assert_called_with(TestObject, 'ACTION', data)

class APITypeTests(tests.TestCase):
    def _test_user_new(self, admin):
        client_obj = mock.Mock()
        client_obj.req.return_value = json.dumps({'id': 'testid',
                                                  'key': 'testkey',
                                                  'admin': admin})
        user = client.User.new(client_obj)
        client_obj.req.assert_called_with(client.User, 'create', {'admin': False})

        self.assertEquals(user.user_id, 'testid')
        self.assertEquals(user.key, 'testkey')
        self.assertEquals(user.admin, admin)
        self.assertEquals(repr(user), "<User object, user_id=u'testid', "
                                      "key=u'testkey', admin=%r>" % user.admin)

    def test_user_new_admin(self):
        self._test_user_new(True)

    def test_user_new_not_admin(self):
        self._test_user_new(False)

class DirectClientTests(tests.TestCase):
    def test_init(self):
        client_obj = client.SurveilrDirectClient({})
        import surveilr.api.server.app
        self.assertEquals(type(client_obj.app),
                          surveilr.api.server.app.SurveilrApplication)

    def test_send_req(self):
        from webob import Request

        api_client = client.SurveilrDirectClient({})
        api_client.app = mock.Mock()
        response = mock.Mock()
        response.body  = 'response'
        api_client.app.return_value = response

        client_response = api_client.send_req('tail', 'METHOD', 'body')

        args = api_client.app.call_args[0]
        self.assertEquals(type(args[0]), Request)

        req = args[0]
        self.assertEquals(req.path, 'tail')
        self.assertEquals(req.method, 'METHOD')
        self.assertEquals(req.body, 'body')
        self.assertEquals(client_response, 'response')
