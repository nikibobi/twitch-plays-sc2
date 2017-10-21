'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from threading import Thread
from collections import deque

import requests
import irc.bot
import numpy

from pysc2.agents import base_agent
from pysc2.lib import actions

class TwitchBot(irc.bot.SingleServerIRCBot):
    prefix = '!'

    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.commands = deque()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)

    def on_welcome(self, c, e):
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        print('Joined ' + self.channel)

    def on_pubmsg(self, c, e):
        if e.arguments[0][:1] == TwitchBot.prefix:
            cmd = e.arguments[0][1:]
            print('> ' + cmd)
            self.commands.append(cmd)
        return

    def has_commands(self):
        return bool(self.commands)

    def next_command(self):
        return self.commands.popleft()

class TwitchAgent(base_agent.BaseAgent):
    def __init__(self):
        super(TwitchAgent, self).__init__()

        with open('.secrets', 'r') as secrets:
            args = secrets.readline().split()
            self.bot = TwitchBot(*args)

        thread = Thread(target=self.bot.start)
        thread.daemon = True
        thread.start()

    def step(self, obs):
        super(TwitchAgent, self).step(obs)
        if self.bot.has_commands():
            line = self.bot.next_command().split(' ')
            name = line[0]
            function = actions.FUNCTIONS[name]
            args = [[int(a) for a in arg.split(',')] for arg in line[1:]]
            return actions.FunctionCall(function.id, args)
        return actions.FunctionCall(actions.FUNCTIONS.no_op.id, [])
