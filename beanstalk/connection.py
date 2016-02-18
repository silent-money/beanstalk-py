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
Connection Manage Module
"""
import os
import socket
import threading
from itertools import chain

from beanstalk.exceptions import BeanstalkConnectionError
from beanstalk.protocol import Command


class Connection(object):

    def __init__(self, host=None, port=None, connect_timeout=socket.getdefaulttimeout()):

        assert host and port, '"host" and "port" cannot be None'

        self._host = host
        self._port = port
        self._connect_timeout = connect_timeout

        self._socket = None

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._connect_timeout)
        self._socket.connect((self._host, self._port))
        self._socket.settimeout(None)

    def disconnect(self):
        if not self._socket:
            return

        try:
            self._socket.sendall(Command.QUIT)
        except:
            pass

        try:
            self._socket.disconnect()
        except socket.error:
            pass
        finally:
            self._socket = None

    def reconnect(self):
        self.disconnect()
        self._connect()

    @property
    def client_socket(self):
        if not self._socket:
            self._connect()
        return self._socket

    @property
    def socket_file(self):
        if not self._socket:
            self._connect()
        return self._socket.makefile('rb')


class ConnectionPool(object):

    def __init__(self, connection_class=Connection, max_connection=None, **connection_kwargs):

        assert isinstance(max_connection, (int, long)) and max_connection > 0

        self._max_connection = max_connection
        self._connection_class = connection_class
        self._connection_kwargs = connection_kwargs

        # Init Pool Info
        self.pid = os.getpid()
        self._created_connections = 0
        self._available_connections = []
        self._in_use_connections = set()
        self._check_lock = threading.Lock()

    def _reset_pool(self):
        """ Reset Pool Info """
        self.pid = os.getpid()
        self._created_connections = 0
        self._available_connections = []
        self._in_use_connections = set()
        self._check_lock = threading.Lock()

    def _check_pid(self):
        """ Make pool threading safe and avoid use in multi-processing """
        if self.pid != os.getpid():
            with self._check_lock:
                if self.pid == os.getpid():
                    # another thread already did the work while we waited
                    # on the lock.
                    return
                self.disconnect_all()
                self._reset_pool()

    def pick_connection(self):
        self._check_pid()
        try:
            connection = self._available_connections.pop()
        except IndexError:
            connection = self.make_connection()

        self._in_use_connections.add(connection)
        return connection

    def make_connection(self):
        """Create a new connection"""
        if self._created_connections >= self._max_connection:
            raise BeanstalkConnectionError("Too many connections")
        self._created_connections += 1
        return self._connection_class(**self._connection_kwargs)

    def release(self, connection):
        """Releases the connection back to the pool"""
        self._check_pid()
        if connection.pid != self.pid:
            return
        self._in_use_connections.remove(connection)
        self._available_connections.append(connection)

    def disconnect_all(self):
        """ Disconnects all connections in the pool """
        all_conns = chain(self._available_connections, self._in_use_connections)
        for connection in all_conns:
            connection.disconnect()
