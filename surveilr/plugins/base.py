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
"""

import json
from webob import Response
from webob.dec import wsgify


class SurveilrPlugin(object):
    def __init__(self, global_config):
        pass

    @wsgify
    def __call__(self, req):
        data = json.loads(req.body)
        metric = {'timestamp': data['timestamp'],
                  'metrics': data['metrics']}
        saved_state = data['saved_state']
        new_saved_state, status = self.run(metric, saved_state)
        return Response(json.dumps({'state': new_saved_state,
                                    'status': status}))

    def run(self, metric, saved_state):
        return None, None  # pragma: nocover
