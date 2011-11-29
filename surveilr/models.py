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

    Model definitions
"""
from riakalchemy import RiakObject
from riakalchemy.types import Integer, String, Dict, RelatedObjects


class Service(RiakObject):
    """A service that is referenced by many LogEntry's

    If the same logical service gets information from multiple sources,
    it needs separate Service objects. However, if several metrics are
    provided for a single service in each log entry, only one Service
    is needed"""
    bucket_name = 'services'
    searchable = True

    name = String()
    most_recent_log_entry = RelatedObjects()


class User(RiakObject):
    """A user of the service"""
    bucket_name = 'users'


class LogEntry(RiakObject):
    """A log entry holding one or more metrics

    A log entry "belongs" to a single Service. Each LogEntry
    can hold multiple metrics, but all LogEntry's must
    have the same set of metrics."""
    bucket_name = 'log_entries'

    timestamp = Integer()
    metrics = Dict()
    service = RelatedObjects(backref=True)

    def post_save(self):
        super(LogEntry, self).post_save()
        service = self.service[0]
        service.most_recent_log_entry = [self]
        service.save()
