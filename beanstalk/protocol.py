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
Beanstalk Protocol
"""


class Command(object):
    QUIT = 'quit\r\n'
    PUT = 'put %d %d %d %d\r\n%s\r\n'
    RESERVE = 'reserve\r\n'
    RESERVE_WITH_TIMEOUT = 'reserve-with-timeout %d\r\n'
    KICK = 'kick %d\r\n'
    KICK_JOB = 'kick-job %d\r\n'
    PEEK = 'peek %d\r\n'
    PEEK_READY = 'peek-ready\r\n'
    PEEK_DELAYED = 'peek-delayed\r\n'
    PEEK_BURIED = 'peek-buried\r\n'
    LIST_TUBES = 'list-tubes\r\n'
    LIST_TUBE_USED = 'list-tube-used\r\n'
    LIST_TUBES_WATCHED = 'list-tubes-watched\r\n'


class Response(object):
    OK = 'OK'
    FOUND = 'FOUND'
    NOT_FOUND = 'NOT_FOUND'
    INSERTED = 'INSERTED'
    JOB_TOO_BIG = 'JOB_TOO_BIG'
    BURIED = 'BURIED'
    DRAINING = 'DRAINING'
    RESERVED = 'RESERVED'
    DEADLINE_SOON = 'DEADLINE_SOON'
    TIMED_OUT = 'TIMED_OUT'
    KICKED = 'KICKED'
    USING = 'USING'




