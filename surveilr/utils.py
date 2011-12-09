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

    Utility functions
"""

import httplib2
import json


def truncate(number, rounding_factor):
    """Truncate to nearest arbitrary multiple

    >>> truncate(1000, 100)
    1000
    >>> truncate(1099, 100)
    1000
    >>> truncate(1099, 50)
    1050
    >>> truncate(1099, 50)
    1050
    """
    return (int(number) / int(rounding_factor)) * int(rounding_factor)


def enhance_data_point(data_point):
    http = httplib2.Http(timeout=10)

    service = data_point.service[0]
    user = service.user[0]

    for plugins in service.plugins:
        saved_state = plugins.get('saved_state', None)
        url = plugins.get('url')
        body = json.dumps({'timestamp': data_point.timestamp,
                           'metrics': data_point.metrics,
                           'service_id': service.key,
                           'user_id': user.key,
                           'saved_state': saved_state})

        http.request(url, method="POST", body=body)
