import json
import mock

from surveilr import tests
from surveilr.api import client


class SurveilrClientTests(tests.TestCase):
    test_url = 'http://somewhere:1234/else'
    test_auth = ('foo', 'bar')

    def _get_client(self, url=None, auth=None):
        if not url:
            url = self.test_url
        if not auth:
            auth = self.test_auth
        return client.SurveilrClient(self.test_url, self.test_auth)

    def test_client_class_actions(self):
        """client.{new,get,delete}_{user,service} proxied to class methods"""

        for op in ['delete', 'new', 'get']:
            for t in ['User', 'Service']:
                @mock.patch('surveilr.api.client.%s' % t)
                def test_action(cls):
                    test_args = ('foo', 'bar', 'baz')
                    test_kwargs = {'foo': 'bar',
                                   'baz': 'wibble'}
                    api_client = self._get_client()
                    client_obj_func = getattr(api_client,
                                              '%s_%s' % (op, t.lower()))

                    user = client_obj_func(*test_args, **test_kwargs)

                    cls_func = getattr(cls, op)
                    cls_func.assert_called_with(api_client, *test_args,
                                                **test_kwargs)
                    self.assertEquals(user, cls_func.return_value)
                test_action()

    @mock.patch('surveilr.api.client.httplib2')
    def test_send_req(self, httplib2):
        # Setup
        api_client = self._get_client()

        class FakeResponse(object):
            def __init__(self, status_code):
                self.status = status_code

        http = httplib2.Http.return_value
        http.request.return_value = (FakeResponse(200), 'resp')

        # Exercise
        client_response = api_client.send_req('tail', 'METHOD', 'body')

        # Verify that the credentials are passed
        http.add_credentials.assert_called_with(*self.test_auth)
        # Verify that the given method is used, the body is passed correctly,
        # and that the url is constructed correctlyi
        http.request.assert_called_with(self.test_url + '/tail',
                                        method='METHOD',
                                        body='body')

        # Verify that the response comes back intact
        self.assertEquals(client_response, 'resp')

    @mock.patch('surveilr.api.client.httplib2')
    def test_send_req_403_reraises_unauthorized_error(self, httplib2):
        # Setup
        api_client = self._get_client()

        class FakeResponse(object):
            reason = 'Just because, ok?'

            def __init__(self, status_code):
                self.status = status_code

        http = httplib2.Http.return_value
        http.request.return_value = (FakeResponse(403), 'resp')

        # Exercise and verify
        self.assertRaises(client.UnauthorizedError,
                          api_client.send_req, 'tail', 'METHOD', 'body')

    def test_req_create_with_parend(self):
        api_client = self._get_client()

        test_data = {'foo': ['bar', 'baz', 2]}

        class FakeObjType(client.APIObject):
            url_part = 'stuff'

        parent = FakeObjType(api_client)
        parent.id = 7
        with mock.patch_object(api_client, 'send_req') as send_req:
            FakeObjType(api_client).req(api_client, 'create', test_data,
                                        parent=parent)
            self.assertEquals(send_req.call_args[0][0], '/stuffs/7/stuffs')
            self.assertEquals(send_req.call_args[1]['method'], 'POST')
            self.assertEquals(json.loads(send_req.call_args[1]['body']),
                              test_data)

    def test_req_create(self):
        api_client = self._get_client()

        test_data = {'foo': ['bar', 'baz', 2]}

        class FakeObjType(client.APIObject):
            url_part = 'stuff'

        with mock.patch_object(api_client, 'send_req') as send_req:
            FakeObjType(api_client).req(api_client, 'create', test_data)
            self.assertEquals(send_req.call_args[0][0], '/stuffs')
            self.assertEquals(send_req.call_args[1]['method'], 'POST')
            self.assertEquals(json.loads(send_req.call_args[1]['body']),
                              test_data)

    def test_req_get(self):
        api_client = self._get_client()

        class FakeObjType(client.APIObject):
            url_part = 'stuff'

        with mock.patch_object(api_client, 'send_req') as send_req:
            FakeObjType(api_client).req(api_client, 'get', 'someid')
            self.assertEquals(send_req.call_args[0][0], '/stuffs/someid')
            self.assertEquals(send_req.call_args[1]['method'], 'GET')

    def test_req_delete(self):
        api_client = self._get_client()

        class FakeObjType(client.APIObject):
            url_part = 'stuff'

        with mock.patch_object(api_client, 'send_req') as send_req:
            FakeObjType(api_client).req(api_client, 'delete', 'someid')
            self.assertEquals(send_req.call_args[0][0], '/stuffs/someid')
            self.assertEquals(send_req.call_args[1]['method'], 'DELETE')


class APIObjectTests(tests.TestCase):
    def _test_req(self):
        client_obj = mock.Mock()
        data = mock.Sentinel()

        class TestObject(client.APIObject):
            url_part = 'test'

        obj = TestObject(client_obj)
        obj.req('ACTION', data)

        client_obj.req.assert_called_with(TestObject, 'ACTION', data)

    def _test_get_or_delete(self, op, req_return=None):
        client_obj = mock.Mock()

        class TestObject(client.APIObject):
            url_part = 'test'

            @classmethod
            def json_deserialise(inner_self, client, s):
                self.assertEquals(s, 'lots of json')

            req = mock.Mock()

        TestObject.req.return_value = req_return

        getattr(TestObject, op)(client_obj, 'testid')
        TestObject.req.assert_called_with(client_obj, op, 'testid')

    def test_delete(self):
        self._test_get_or_delete('delete')

    def test_get(self):
        self._test_get_or_delete('get', 'lots of json')


class UserTests(tests.TestCase):
    def _test_new(self, admin):
        # Setup
        client_obj = mock.Mock()
        with mock.patch_object(client.User, 'req') as client_req:
            client_req.return_value = json.dumps({'id': 'testid',
                                                  'key': 'testkey',
                                                  'admin': admin})

            # Exercise
            user = client.User.new(client_obj)

            # Verify
            client_req.assert_called_with(client_obj, 'create',
                                          {'admin': False})

            self.assertEquals(user.id, 'testid')
            self.assertEquals(user.key, 'testkey')
            self.assertEquals(user.admin, admin)
            self.assertEquals(repr(user), "<User object, id=u'testid', "
                                          "key=u'testkey', admin=%r>" %
                                          user.admin)

    def test_user_new_admin(self):
        self._test_new(True)

    def test_user_new_not_admin(self):
        self._test_new(False)


class ServiceTests(tests.TestCase):
    def test_new(self):
        # Setup
        test_plugins = ['http://h:1/p']
        client_obj = mock.Mock()
        with mock.patch_object(client.Service, 'req') as service_req:
            service_req.return_value = json.dumps({'id': 'testid',
                                                  'name': 'testname',
                                                  'plugins': test_plugins})

            # Exercise
            service = client.Service.new(client_obj, 'testname',
                                         plugins=test_plugins)

            # Verify
            service_req.assert_called_with(client_obj, 'create',
                                           {'name': 'testname',
                                            'plugins': test_plugins})

            self.assertEquals(service.id, 'testid')
            self.assertEquals(service.name, 'testname')
            self.assertEquals(service.plugins, test_plugins)
            self.assertEquals(repr(service), "<Service object, id=u'testid', "
                                              "name=u'testname', "
                                              "plugins=[u'http://h:1/p']>")


class MetricTests(tests.TestCase):
    def test_service_metric_new(self):
        # Setup
        client_obj = mock.Mock()
        service_obj = client.Service(client_obj, id='testid',
                                     name='testname', plugins=[])

        with mock.patch_object(client, 'Metric') as Metric:
            service_obj.new_metric({'foo': 1234})

            Metric.new.assert_called_with(client_obj, service_obj,
                                          {'foo': 1234})


    def test_new(self):
        # Setup
        client_obj = mock.Mock()
        service_obj = mock.Sentinel()
        with mock.patch_object(client.Metric, 'req') as metric_req:
            metric_req.return_value = json.dumps({})

            # Exercise
            client.Metric.new(client_obj, service_obj, {'something': 1234})

            # Verify
            metric_req.assert_called_with(client_obj,
                                          'create',
                                          {'metrics': {'something': 1234}},
                                          parent=service_obj)


class DirectClientTests(tests.TestCase):
    def test_init(self):
        client_obj = client.SurveilrDirectClient({})
        import surveilr.api.server.app
        self.assertEquals(type(client_obj.app),
                          surveilr.api.server.app.SurveilrApplication)

    def test_send_req(self):
        from webob import Request

        api_client = client.SurveilrDirectClient({})
        with mock.patch_object(api_client, 'app') as app:
            response = mock.Mock()
            response.body = 'response'
            app.return_value = response

            client_response = api_client.send_req('tail', 'METHOD', 'body')

            args = app.call_args[0]
            self.assertEquals(type(args[0]), Request)

            req = args[0]
            self.assertEquals(req.path, 'tail')
            self.assertEquals(req.method, 'METHOD')
            self.assertEquals(req.body, 'body')
            self.assertEquals(client_response, 'response')
