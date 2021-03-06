#!/usr/bin/python
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

    API server implementation
"""

import eventlet
import eventlet.wsgi
import functools
import json
import time

import riakalchemy
from routes import Mapper
from routes.util import URLGenerator

from webob import exc
from webob import Response
from webob.dec import wsgify
from webob.exc import HTTPNotFound
from webob.exc import HTTPForbidden

from surveilr import config
from surveilr import messaging
from surveilr import models
from surveilr import utils


def is_privileged(req):
    if 'surveilr.user' in req.environ:
        return req.environ['surveilr.user'].credentials['admin']
    # This feels pretty scary
    return True


def privileged(f):
    @functools.wraps(f)
    def wrapped(self, req, *args, **kwargs):
        if is_privileged(req):
            return f(self, req, *args, **kwargs)
        else:
            return HTTPForbidden()
    return wrapped


class Controller(object):
    @classmethod
    def dictify(cls, obj):  # pragma: nocover
        return {}

    @classmethod
    def json_serialise(self, obj):
        return json.dumps(self.dictify(obj))


class NotificationController(Controller):
    """Routes style controller for notifications"""

    def create(self, req, user_id):
        """Called for POST requests to /user/{id}/notifications

        Sends a notification to the given user"""

        user = models.User.get(key=user_id)
        messaging.send(user, json.loads(req.body))
        response = {}
        return Response(json.dumps(response))


class UserController(Controller):
    """Routes style controller for actions related to users"""

    @classmethod
    def dictify(cls, user):
        return {'id': user.key,
                'key': user.api_key,
                'messaging_driver': getattr(user, 'messaging_driver', None),
                'messaging_address': getattr(user, 'messaging_address', None),
                'admin': user.credentials.get('admin', False)}

    @privileged
    def create(self, req):
        """Called for POST requests to /users

        Creates the user, returns a JSON object with the ID assigned
        to the user"""
        data = json.loads(req.body)

        obj_data = {}

        obj_data['credentials'] = {}

        if 'admin' in data:
            obj_data['credentials']['admin'] = data['admin']

        for key in ['messaging_driver', 'messaging_address']:
            if key in data:
                obj_data[key] = data[key]

        user = models.User(**obj_data)
        user.save()
        return Response(self.json_serialise(user))

    @privileged
    def show(self, req, id):
        """Called for GET requests to /users/{id}

        Returns information for the given service"""
        try:
            user = models.User.get(id)
            return Response(self.json_serialise(user))
        except riakalchemy.NoSuchObjectError:
            return HTTPNotFound()

    @privileged
    def delete(self, req, id):
        """Called for DELETE requests to /users/{id}

        Delete the given user"""

        models.User.get(id).delete()
        return Response('')


class ServiceController(Controller):
    """Routes style controller for actions related to services"""

    @classmethod
    def dictify(cls, service):
        d = {'id': service.key,
             'name': service.name}

        if getattr(service, 'plugins', None):
            d['plugins'] = [p['url'] for p in getattr(service, 'plugins', [])]
        else:
            d['plugins'] = []

        return d

    def create(self, req):
        """Called for POST requests to /services

        Creates the service, returns a JSON object with the ID assigned
        to the service"""
        data = json.loads(req.body)

        data['user'] = [req.environ['surveilr.user']]

        if 'plugins' not in data or not data['plugins']:
            data['plugins'] = []

        service = models.Service(**data)
        service.save()
        return Response(self.json_serialise(service))

    def show(self, req, id):
        """Called for GET requests to /services/{id}

        Returns information for the given service"""
        try:
            service = models.Service.get(id)
            return Response(self.json_serialise(service))
        except riakalchemy.NoSuchObjectError:
            return HTTPNotFound()

    def delete(self, req, id):
        """Called for DELETE requests to /services/{id}

        Delete the given service"""
        models.Service.get(id).delete()
        return Response('')

    def update(self, req, id):
        data = json.loads(req.body)

        service = models.Service.get(id)

        # Plugins
        plugin_states = dict((p['url'], p['saved_state'])
                                 for p in getattr(service, 'plugins', []))

        service.plugins = [{'url': url,
                           'saved_state': plugin_states.get(url, None)}
                               for url in data['plugins']]
        service.save()
        return Response('')


class MetricController(Controller):
    """Routes style controller for actions related to log entries"""
    def create(self, req, service_name):
        """Called for POST requests to /services/{id}/metrics

        Logs a measurement against the service identified by {id}.
        Returns an empty response"""

        data = json.loads(req.body)
        service = models.Service.get(service_name)
        data['service'] = [service]
        data['timestamp'] = utils.truncate(time.time(), 60)
        log_entry = models.LogEntry(**data)
        log_entry.save()
        eventlet.spawn_n(utils.enhance_data_point, log_entry)
        return Response(json.dumps({}))

    def index(self, req, service_name):
        """Called for GET requests to /services/{id}/metrics

        Returns a list of metrics logged against the service identified
        by {id}."""
        service = models.Service.get(service_name)
        retval = []
        for x in models.LogEntry.get(service=service).all():
            retval += [{'metrics': x.metrics, 'timestamp': x.timestamp}]
        return Response(json.dumps(retval))


class SurveilrApplication(object):
    """The core Surveilr Monitoring WSGI application"""
    controllers = {}

    map = Mapper()
    map.resource("metric", "metrics", controller='MetricController',
                 path_prefix='/services/{service_name}')
    map.resource("service", "services", controller='ServiceController')
    map.resource("user", "users", controller='UserController')
    map.resource("notification", "notifications",
                 controller='NotificationController',
                 path_prefix='/users/{user_id}')

    def __init__(self, global_config):
        riak_host = config.get_str('riak', 'host')
        riak_port = config.get_int('riak', 'port')

        riakalchemy.connect(host=riak_host, port=riak_port)

    @wsgify
    def __call__(self, req):
        """Where it all happens

        Using the Mapper object, it finds the relevant controller
        based on the URL and delegates the call to that."""

        results = self.map.routematch(environ=req.environ)
        if not results:
            return exc.HTTPNotFound()
        match, route = results
        link = URLGenerator(self.map, req.environ)
        req.urlvars = ((), match)
        kwargs = match.copy()
        controller = globals()[kwargs.pop('controller')]()
        method = kwargs.pop('action')
        req.link = link
        req.route_name = route.name

        return getattr(controller, method)(req, **kwargs)


def server_factory(global_conf, host, port):
    port = int(port)

    def serve(app):
        socket = eventlet.listen((host, port))
        eventlet.wsgi.server(socket, app)
    return serve


def main():
    server_factory({}, '', 9877)(SurveilrApplication({}))


if __name__ == '__main__':  # pragma: nocover
    main()
