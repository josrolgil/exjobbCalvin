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

from calvin.actor.actor import Actor, ActionResult, condition, guard, manage


class Alternate(Actor):
    """
    Alternating between two streams of tokens
    Inputs:
      token_1 : first token stream
      token_2 : second token stream
    Outputs:
        token : resulting token stream
    """

    @manage(['token_one'])
    def init(self):
        self.token_one = True

    def is_even(self, input):
        return self.token_one

    def is_odd(self, input):
        return not self.is_even(input)

    @condition(['token_1'], ['token'])
    @guard(is_even)
    def port_one(self, input):
        self.token_one = False
        return ActionResult(production=(input, ))

    @condition(['token_2'], ['token'])
    @guard(is_odd)
    def port_two(self, input):
        self.token_one = True
        return ActionResult(production=(input, ))

    action_priority = (port_one, port_two)

    test_set = [
        {
            'in': {'token_1': [1, 2], 'token_2': ['a', 'b']},
            'out': {'token': [1, 'a', 2, 'b']}
        },
        {
            'in': {'token_1': [1]},
            'out': {'token': [1]}
        }
    ]
