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

    Tests for configuration module
"""

import json
from webob import Request

from surveilr import tests
from surveilr.plugins import base


class PluginTests(tests.TestCase):
    def test_base(self):
        metrics = {'duration': 85000,
                   'response_size': 12435}
        timestamp = 13217362355575
        saved_state = {'what': 'ever',
                       'you': 'prefer'}

        class TestPlugin(base.SurveilrPlugin):
            def run(self2, metrics_in, saved_state_in):
                self.assertEquals(metrics_in['metrics'], metrics)
                self.assertEquals(metrics_in['timestamp'], timestamp)
                self.assertEquals(saved_state_in, saved_state)
                return 'New saved state', 'The status'

        test_plugin = TestPlugin({})
        req = Request.blank('',
                            method='POST',
                            POST=json.dumps({
                                   'timestamp': timestamp,
                                   'service_id': 'NUD2opa92uFD9JaFefXktCxzEUW',
                                   'user_id': 'DYRKd63MjksWEy844DDfFkspwez',
                                   'metrics': metrics,
                                   'saved_state': saved_state}))

        res = test_plugin(req)
        res_obj = json.loads(res.body)
        self.assertEquals(res_obj['status'], 'The status')
        self.assertEquals(res_obj['state'], 'New saved state')
