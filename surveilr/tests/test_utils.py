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

    Plugin tests
"""

import json
import time
import mock

from surveilr import models
from surveilr import tests
from surveilr import utils


class UtilsTests(tests.TestCase):
    def test_enhance(self):
        url = 'http://some-url:345/fooo'
        timestamp = int(time.time() * 1000)
        metrics = {'time': 773,
                   'size': 12554}
        new_state = ['somestate']

        # Create the user, service and log entry
        user = models.User()
        user.save()
        user_id = user.key

        service = models.Service()
        service.user = [user]
        service.plugins = [{'url': url}]
        service.save()
        service_id = service.key

        log_entry = models.LogEntry()
        log_entry.service = [service]

        log_entry.timestamp = timestamp
        log_entry.metrics = metrics.copy()
        log_entry.save()

        with mock.patch('surveilr.utils.httplib2') as httplib2:
            # Mock out the http calls
            request_call = httplib2.Http.return_value.request
            request_call.return_value = (None,
                                         json.dumps({'state': new_state}))

            # Exercise the SUT
            utils.enhance_data_point(log_entry)

            # Verify everything
            self.assertEquals(request_call.call_args[0], (url,), 'Wrong url')
            self.assertEquals(len(request_call.call_args[1]), 2,
                              'Wrong number of kwargs')

            self.assertIn('method', request_call.call_args[1],
                          'No method passed to request call')
            self.assertEquals(request_call.call_args[1]['method'], 'POST',
                              'method was not set to "POST"')

            self.assertIn('body', request_call.call_args[1],
                          'No body passed to request call')
            body = request_call.call_args[1]['body']

            self.assertDictEqual(json.loads(body), {'timestamp': timestamp,
                                                    'service_id': service_id,
                                                    'user_id': user_id,
                                                    'metrics': metrics,
                                                    'saved_state': None})

            self.assertEquals(len(service.plugins), 1)
            self.assertDictEqual(service.plugins[0],
                                 {'url': url, 'saved_state': new_state})

    def test_truncate(self):
        self.assertEquals(utils.truncate(133, 1), 133)
        self.assertEquals(utils.truncate(133, 10), 130)
        self.assertEquals(utils.truncate(133, 20), 120)
        self.assertEquals(utils.truncate(133, 100), 100)
        self.assertEquals(utils.truncate(133, 200), 0)
