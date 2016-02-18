#!/usr/bin/env python
# coding: utf8
#
# Copyright 2016 hdd
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Client Talk with beanstalk
"""
import sys
import yaml

from beanstalk.connection import ConnectionPool
from beanstalk.exceptions import BeanstalkConnectionError, BeanstalkCommandFailed, BeanstalkUnknownError, BeanstalkJobDeadlineSoon
from beanstalk.job import Job
from beanstalk import macro
from beanstalk.protocol import Command, Response


class Beanstalk(object):

    def __init__(self, host='localhost', port=11300, **kwargs):

        self._connection_pool = ConnectionPool(host=host, port=port, **kwargs)

    def _request(self, connection, command, oks, errs):
        connection.client_socket.sendall(command)

        line = connection.socket_file.readline()
        if not line:
            raise BeanstalkConnectionError()
        response = line.split()
        status = response[0]
        results = response[1:]

        if status in oks:
            return results
        elif status in errs:
            raise BeanstalkCommandFailed(command.split()[0], status, response)
        else:
            raise BeanstalkUnknownError(command.split()[0], status, results)

    def _response(self, connection, size):
        body = connection.socket_file.read(size)
        if size > 0 and not body:
            raise BeanstalkConnectionError()
        return body

    def _request_value(self, command, oks, errs=()):
        connection = self._connection_pool.pick_connection()
        value = self._request(connection, command, oks, errs)
        self._connection_pool.release(connection)
        return value[0]

    def _request_job(self, command, oks, errs=(), reserved=True):
        connection = self._connection_pool.pick_connection()
        job_id, size = self._request(connection, command, oks, errs)
        body = self._response(connection, int(size))
        self._connection_pool.release(connection)
        return Job(int(job_id), body, reserved)

    def _request_yaml(self, command, oks, errs=(), reserved=True):
        connection = self._connection_pool.pick_connection()
        job_id, size = self._request(connection, command, oks, errs)
        body = self._response(connection, int(size))
        self._connection_pool.release(connection)
        return yaml.load(body)

    def _request_peek(self, command):
        try:
            return self._request_job(command, [Response.FOUND], [Response.NOT_FOUND], False)
        except BeanstalkCommandFailed:
            return None

    def put(self, body, priority=macro.PRIORITY, delay=0, ttr=macro.TTR):
        """Put a job into the current tube. Returns job id."""
        assert isinstance(body, str), 'Job body must be a str instance'
        jid = self._request_value(Command.PUT % (priority, delay, ttr, len(body), body),
                                  (Response.INSERTED, ),
                                  (Response.JOB_TOO_BIG, Response.BURIED, Response.DRAINING))
        return int(jid)

    def reserve(self, timeout=None):
        """Reserve a job from one of the watched tubes, with optional timeout
        in seconds. Returns a Job object, or None if the request times out."""
        if timeout is not None:
            command = Command.RESERVE_WITH_TIMEOUT % timeout
        else:
            command = Command.RESERVE
        try:
            return self._request_job(command,
                                     (Response.RESERVED, ),
                                     (Response.DEADLINE_SOON, Response.TIMED_OUT))
        except BeanstalkCommandFailed:
            exc = sys.exc_info()[1]
            _, status, results = exc.args
            if status == Response.TIMED_OUT:
                return None
            elif status == Response.DEADLINE_SOON:
                raise BeanstalkJobDeadlineSoon(results)

    def kick(self, bound=1):
        """Kick at most bound jobs into the ready queue."""
        return int(self._request_value(Command.KICK % bound, (Response.KICKED, )))

    def kick_job(self, jid):
        """Kick a specific job into the ready queue."""
        self._request_value(Command.KICK_JOB % jid, (Response.KICKED, ), (Response.NOT_FOUND, ))

    def peek(self, jid):
        """Peek at a job. Returns a Job, or None."""
        return self._request_peek(Command.PEEK % jid)

    def peek_ready(self):
        """Peek at next ready job. Returns a Job, or None."""
        return self._request_peek(Command.PEEK_READY)

    def peek_delayed(self):
        """Peek at next delayed job. Returns a Job, or None."""
        return self._request_peek(Command.PEEK_DELAYED)

    def peek_buried(self):
        """Peek at next buried job. Returns a Job, or None."""
        return self._request_peek(Command.PEEK_BURIED)

    def tubes(self):
        """Return a list of all existing tubes."""
        return self._request_yaml(Command.LIST_TUBES, (Response.OK, ))

    def using(self):
        """Return the tube currently being used."""
        return self._request_value(Command.LIST_TUBE_USED, ['USING'])

    def use(self, name):
        """Use a given tube."""
        return self._request_value('use %s\r\n' % name, (Response.USING, ))

    def watching(self):
        """Return a list of all tubes being watched."""
        return self._request_yaml(Command.LIST_TUBES_WATCHED, ['OK'])

    def watch(self, name):
        """Watch a given tube."""
        return int(self._request_value('watch %s\r\n' % name, ['WATCHING']))

    def ignore(self, name):
        """Stop watching a given tube."""
        try:
            return int(self._request_value('ignore %s\r\n' % name,
                                            ['WATCHING'],
                                            ['NOT_IGNORED']))
        except BeanstalkCommandFailed:
            return 1

    def stats(self):
        """Return a dict of beanstalkd statistics."""
        return self._request_yaml('stats\r\n', ['OK'])

    def stats_tube(self, name):
        """Return a dict of stats about a given tube."""
        return self._request_yaml('stats-tube %s\r\n' % name,
                                   ['OK'],
                                   ['NOT_FOUND'])

    def pause_tube(self, name, delay):
        """Pause a tube for a given delay time, in seconds."""
        self._request_value('pause-tube %s %d\r\n' % (name, delay),
                       ['PAUSED'],
                       ['NOT_FOUND'])

    # -- job interactors --

    def delete(self, jid):
        """Delete a job, by job id."""
        self._request_value('delete %d\r\n' % jid, ['DELETED'], ['NOT_FOUND'])

    def release(self, jid, priority=macro.PRIORITY, delay=0):
        """Release a reserved job back into the ready queue."""
        self._request_value('release %d %d %d\r\n' % (jid, priority, delay),
                       ['RELEASED', 'BURIED'],
                       ['NOT_FOUND'])

    def bury(self, jid, priority=macro.PRIORITY):
        """Bury a job, by job id."""
        self._request_value('bury %d %d\r\n' % (jid, priority),
                       ['BURIED'],
                       ['NOT_FOUND'])

    def touch(self, jid):
        """Touch a job, by job id, requesting more time to work on a reserved
        job before it expires."""
        self._request_value('touch %d\r\n' % jid, ['TOUCHED'], ['NOT_FOUND'])

    def stats_job(self, jid):
        """Return a dict of stats about a job, by job id."""
        return self._request_yaml('stats-job %d\r\n' % jid,
                                   ['OK'],
                                   ['NOT_FOUND'])
