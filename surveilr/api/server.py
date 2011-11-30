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

    Log collection server implementation
"""

import eventlet
import eventlet.wsgi
import json
import time

import riakalchemy
from routes import Mapper
from routes.util import URLGenerator

from webob import exc
from webob import Response
from webob.dec import wsgify
from webob.exc import HTTPNotFound

from surveilr import messaging
from surveilr import models
from surveilr import utils


class NotificationController(object):
    """Routes style controller for notifications"""

    def create(self, req, user_id):
        """Called for POST requests to /user/{id}/notifications

        Sends a notification to the given user"""

        user = models.User.get(key=user_id)
        messaging.send(user, json.loads(req.body))
        response = {}
        return Response(json.dumps(response))


class UserController(object):
    """Routes style controller for actions related to users"""

    def create(self, req):
        """Called for POST requests to /users

        Creates the user, returns a JSON object with the ID assigned
        to the user"""
        data = json.loads(req.body)
        user = models.User(**data)
        user.save()
        response = {'id': user.key}
        return Response(json.dumps(response))

    def show(self, req, id):
        """Called for GET requests to /users/{id}

        Returns information for the given service"""
        try:
            user = models.User.get(id)
            resp_dict = {'id': user.key,
                         'messaging_driver': user.messaging_driver,
                         'messaging_address': user.messaging_address}
            return Response(json.dumps(resp_dict))
        except riakalchemy.NoSuchObjectError:
            return HTTPNotFound()

    def delete(self, req, id):
        """Called for DELETE requests to /users/{id}

        Delete the given user"""
        models.User.get(id).delete()
        return Response('')


class ServiceController(object):
    """Routes style controller for actions related to services"""

    def create(self, req):
        """Called for POST requests to /services

        Creates the service, returns a JSON object with the ID assigned
        to the service"""
        data = json.loads(req.body)
        service = models.Service(**data)
        service.save()
        response = {'id': service.key}
        return Response(json.dumps(response))

    def show(self, req, id):
        """Called for GET requests to /services/{id}

        Returns information for the given service"""
        try:
            service = models.Service.get(id)
            return Response({'id': service.key})
        except riakalchemy.NoSuchObjectError:
            return HTTPNotFound()

    def delete(self, req, id):
        """Called for DELETE requests to /services/{id}

        Delete the given service"""
        models.Service.get(id).delete()
        return Response('')


class MetricController(object):
    """Routes style controller for actions related to log entries"""
    def create(self, req, service_name):
        """Called for POST requests to /services/{id}/metrics

        Logs a measurement against the service identified by {id}.
        Returns an empty response"""
        data = json.loads(req.body)
        service = models.Service.get(service_name)
        data['service'] = [service]
        data['timestamp'] = utils.truncate(time.time(), 60)
        models.LogEntry(**data).save()
        return Response('')

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

application = SurveilrApplication()


def main():
    socket = eventlet.listen(('', 9877))
    eventlet.wsgi.server(socket, application)


if __name__ == '__main__':  # pragma: nocover
    main()
