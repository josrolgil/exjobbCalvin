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

from calvin.actor.actor import Actor, ActionResult, manage, condition

class Print(Actor):
    """
    Print tokens to suitable device

    Input:
      token : Any token
    """

    def exception_handler(self, action, args, context):
        # Check args to verify that it is EOSToken
        return action(self, *args)

    @manage()
    def init(self):
        pass

    @condition(action_input=['token'])
    def action(self, token):
        print str(token).strip()
        return ActionResult()

    action_priority = (action, )

