# -*- coding: utf-8 -*-

# Copyright (c) 2015 Ericsson AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import time

from calvin.actor.actor import ActionResult
from calvin.runtime.south.plugins.async import async
from calvin.utilities.calvinlogger import get_logger

_log = get_logger(__name__)


class Scheduler(object):

    """docstring for Scheduler"""

    def __init__(self, node, actor_mgr, monitor):
        super(Scheduler, self).__init__()
        self.actor_mgr = actor_mgr
        self.idle = False
        self.done = False
        self.node = node
        self.monitor = monitor
        self.delayed_loop = None
        self._loop_once = None
        self._trigger_set = set()
        self._heartbeat_loop = None
        self._heartbeat = 1

    def run(self):
        async.run_ioloop()

    def stop(self):
        if not self.done:
            async.DelayedCall(0, async.stop_ioloop)
        self.done = True

    def loop_once(self, all_=False):
        activity = self.monitor.loop(self)

        # If all ignore the set
        if all_:
            total = self.fire_actors(None)
        else:
            total = self.fire_actors(self._trigger_set)

        self._loop_once = None

        local_trigger_set = self._trigger_set
        self._trigger_set = set()

        activity = total.did_fire or activity

        _log.debug("looped_once for %s at %s again in %s" %
                   ("ALL" if all_ else local_trigger_set, time.time(), 0 if activity else self._heartbeat))

        if activity:
            # Something happened - run again
            self.trigger_loop(0, total.actor_ids)
        else:
            # No firings, wait a while until next loop
            if self._heartbeat_loop is not None:
                self._heartbeat_loop.cancel()
            self._heartbeat_loop = async.DelayedCall(self._heartbeat, self.trigger_loop)

    def trigger_loop(self, delay=0, actor_ids=None):
        """ Trigger the loop_once potentially after waiting delay seconds """

        if delay > 0:
            _log.debug("Delayed trigger %s" % delay)
            async.DelayedCall(delay, self.loop_once, True)
        else:
            # Never have more then one outstanding loop_once

            if actor_ids is None:
                if self._loop_once is not None:
                    self._loop_once.cancel()
                self._loop_once = async.DelayedCall(0, self.loop_once, True)
            else:
                self._trigger_set.update(actor_ids)

                # Dont run None jobs
                if self._trigger_set == set([None]):
                    _log.debug("Ignoring fire")
                    return

                _log.debug(self._trigger_set)
                if self._loop_once is None:
                    self._loop_once = async.DelayedCall(0, self.loop_once)

    def _log_exception_during_fire(self, e):
        _log.exception(e)

    def fire_actors(self, actor_ids=None):
        total = ActionResult(did_fire=False)
        total.actor_ids = set()

        for actor in self.actor_mgr.enabled_actors():
            # if actor_ids is not None and actor.id not in actor_ids:
            #     _log.debug("ignoring actor %s(%s)" % (actor._type, actor.id))
            #     continue
            try:
                action_result = actor.fire()
                _log.debug("fired actor %s(%s)" % (actor._type, actor.id))
                total.merge(action_result)
                total.actor_ids.add(actor.id)
            except Exception as e:
                self._log_exception_during_fire(e)
        self.idle = not total.did_fire
        return total


class DebugScheduler(Scheduler):
    """This is an instrumented version of the scheduler for use in debugging runs."""

    def __init__(self, node, actor_mgr, monitor):
        super(DebugScheduler, self).__init__(node, actor_mgr, monitor)

    def trigger_loop(self, delay=0, actor_ids=None):
        import inspect
        import traceback
        super(DebugScheduler, self).trigger_loop(delay, actor_ids)
        (frame, filename, line_no, fname, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        _log.debug("triggered %s by %s in file %s at %s" % (time.time(), fname, filename, line_no))
        _log.debug("Trigger happend here:\n" + ''.join(traceback.format_stack()[-6:-1]))

    def _log_exception_during_fire(self, e):
        from infi.traceback import format_exception
        _log.error('\n'.join(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))

    def fire_actors(self, actor_ids=None):
        from infi.traceback import traceback_context
        traceback_context()
        return super(DebugScheduler, self).fire_actors(actor_ids)
