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

from calvin.actor.actor import Actor, manage, condition, ActionResult


def value_for_key(d, keypath):
    keylist = keypath.split('.')
    res = d
    for key in keylist:
        res = res[key]
    return res


class Format(Actor):

    """
    Format output according to 'fmt' using dict

    Format string uses \"{access.key.path}\" to access dict

    Inputs:
      dict :
    Outputs:
      text : Formatted string
    """

    REGEX = r"{(.+?)}"

    @manage(['fmt', 'fmtkeys'])
    def init(self, fmt):
        self.fmt = fmt
        self.use('calvinsys.native.python-re', shorthand="regex")
        self.fmtkeys = self['regex'].findall(Format.REGEX, fmt)

    @condition(['dict'], ['text'])
    def action(self, d):
        res = {}
        try:
            for fmtkey in self.fmtkeys:
                res[fmtkey] = value_for_key(d, fmtkey)
        except Exception:
            res = {}
        retval = self.fmt
        for key, value in res.iteritems():
            retval = retval.replace('{' + key + '}', str(value))

        return ActionResult(production=(retval, ))

    action_priority = (action, )
    requires = ['calvinsys.native.python-re']

    test_args = ["{huey.dewey.louie}"]
    test_set = [
        {'in': {'dict': [{'huey': {'dewey': {'louie': 'gotcha!'}}}]}},
        {'out': {'text': ['gotcha!']}}
    ]
