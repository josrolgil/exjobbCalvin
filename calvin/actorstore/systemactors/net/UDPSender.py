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

from calvin.utilities.calvinlogger import get_logger

_log = get_logger(__name__)


class UDPSender(Actor):
    """
    Send all incoming tokens to given address/port over UDP

    Control port takes control commands of the form (uri only applicable for connect.)

    {
        "command" : "connect"/"disconnect",
        "uri": "udp://<address>:<port>"
    }


    Input:
      data_in : Each received token will be sent to address set via control port
      control_in : Control port
    """

    @manage(['address', 'port'])
    def init(self):
        self.address = None
        self.port = None
        self.sender = None
        self.setup()

    def connect(self):
        self.sender = self['socket'].connect(self.address, self.port, connection_type="UDP")

    def will_migrate(self):
        if self.sender:
            self.sender.disconnect()

    def did_migrate(self):
        self.setup()
        if self.address is not None:
            self.connect()

    def setup(self):
        self.use('calvinsys.network.socketclienthandler', shorthand='socket')
        self.use('calvinsys.native.python-re', shorthand='regexp')

    @condition(action_input=['data_in'])
    @guard(lambda self, token: self.sender)
    def send(self, token):
        self.sender.send(token)
        return ActionResult(production=())

    # URI parsing - 0: protocol, 1: host, 2: port
    URI_REGEXP = r'([^:]+)://([^/:]*):([0-9]+)'

    def parse_uri(self, uri):
        status = False
        try:
            parsed_uri = self['regexp'].findall(self.URI_REGEXP, uri)[0]
            protocol = parsed_uri[0]
            if protocol != 'udp':
                _log.warn("Protocol '%s' not supported, assuming udp" % (protocol,))
            self.address = parsed_uri[1]
            self.port = int(parsed_uri[2])
            status = True
        except:
            _log.warn("malformed or erroneous control uri '%s'" % (uri,))
            self.address = None
            self.port = None
        return status

    @condition(action_input=['control_in'])
    @guard(lambda self, control: control.get('command', '') == 'connect' and not self.sender)
    def new_connection(self, control):
        print control
        if self.parse_uri(control.get('uri', '')):
            self.connect()

        return ActionResult(production=())

    @condition(action_input=['control_in'])
    @guard(lambda self, control: control.get('control', '') == 'disconnect' and self.sender)
    def close_connection(self, control):
        self.sender.disconnect()
        del self.sender
        self.sender = None
        return ActionResult(production=())

    action_priority = (new_connection, close_connection, send)
    requires = ['calvinsys.network.socketclienthandler', 'calvinsys.native.python-re', 'calvinsys.native.python-json']
