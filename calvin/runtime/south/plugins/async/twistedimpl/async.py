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

from twisted.internet import reactor


class DelayedCall(object):

    def __init__(self, delay, callback, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self.delay = delay
        self.callback = callback
        self.reset()

    def reset(self):
        self.delayedCall = reactor.callLater(self.delay, self.callback, *self._args, **self._kwargs)

    def cancel(self):
        if self.delayedCall.active():
            self.delayedCall.cancel()


def run_ioloop():
    reactor.run()


def stop_ioloop():
    reactor.stop()


# Thread function
call_from_thread = reactor.callFromThread
