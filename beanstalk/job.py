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
Job Manage Module
"""


class Job(object):
    def __init__(self, jid, body, reserved=True):
        self.jid = jid
        self.body = body
        self.reserved = reserved

    # def _priority(self):
    #     stats = self.stats()
    #     if isinstance(stats, dict):
    #         return stats['pri']
    #     return macro.PRIORITY

    # def delete(self):
    #     """Delete this job."""
    #     self.conn.delete(self.jid)
    #     self.reserved = False
    #
    # def release(self, priority=None, delay=0):
    #     """Release this job back into the ready queue."""
    #     if self.reserved:
    #         self.conn.release(self.jid, priority or self._priority(), delay)
    #         self.reserved = False
    #
    # def bury(self, priority=None):
    #     """Bury this job."""
    #     if self.reserved:
    #         self.conn.bury(self.jid, priority or self._priority())
    #         self.reserved = False

    # def kick(self):
    #     """Kick this job alive."""
    #     self.conn.kick_job(self.jid)
    #
    # def touch(self):
    #     """Touch this reserved job, requesting more time to work on it before
    #     it expires."""
    #     if self.reserved:
    #         self.conn.touch(self.jid)
    #
    # def stats(self):
    #     """Return a dict of stats about this job."""
    #     return self.conn.stats_job(self.jid)
