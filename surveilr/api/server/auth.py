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

    API server auth implementation
"""

from webob.dec import wsgify
from webob.exc import HTTPUnauthorized

from surveilr import models
from riakalchemy import NoSuchObjectError


def require_auth_middleware_factory(global_config):
    @wsgify.middleware
    def require_auth_middleware(req, app):
        if 'repoze.who.identity' not in req.environ:
            raise HTTPUnauthorized()
        return app
    return require_auth_middleware


class SurveilrAuthPlugin(object):
    def authenticate(self, environ, identity):
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None

        try:
            user = models.User.get(key=login)
        except NoSuchObjectError:
            return None

        if user.api_key == password:
            environ['surveilr.user'] = user
            return login
        return None
