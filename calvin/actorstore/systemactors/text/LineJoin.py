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

from calvin.actor.actor import Actor, ActionResult, manage, condition, guard
from calvin.runtime.north.calvin_token import EOSToken, ExceptionToken


class LineJoin(Actor):
    """
    Join strings into a text token using delimiter 'delim' (defaults to '\\n')

    Consume consecutive strings until an end-of-stream (EOSToken) is received,
    which triggers an output of the joined lines. After receiving the EOFToken,
    the LineJoin is reset and ready for new lines to join.

    Inputs:
      line : arbitrary string
    Outputs:
      text : strings joined by
    """
    @manage(['lines', 'delim', 'text'])
    def init(self, delim='\n'):
        self.delim = delim
        self.lines = []
        self.text = None

    def exception_handler(self, action, args, context):
        # FIXME: Check that action is append and args is EOSToken
        #        if not, call super's exception_handler
        #        Similarly, if self.text is not None => raise
        self.text = self.delim.join(self.lines)
        self.lines = []
        return ActionResult()

    @condition([], ['text'])
    @guard(lambda self: self.text is not None)
    def produce(self):
        text = self.text
        self.text = None
        return ActionResult(production=(text,))

    @condition(['line'], [])
    @guard(lambda self, token: self.text is None)
    def append(self, token):
        self.lines.append(token)
        return ActionResult()

    action_priority = (produce, append, )

