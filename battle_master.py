import asyncio

import discord
import logging
import sqlite3
from datetime import datetime


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('battle_master.db')
        self.c = self.conn.cursor()

    # Player database methods
    def player_exists(self, name):
        self.c.execute("SELECT EXISTS(SELECT 1 FROM players WHERE name=:name)", {"name": name})
        if self.c.fetchone() == (1,):
            return True
        else:
            return False

    def add_player(self, name):
        self.c.execute("INSERT INTO players VALUES (:name, 1000, 0, 0, 0, 'Player')", {"name": name})
        self.conn.commit()

    def remove_player(self, name):
        self.c.execute('''DELETE FROM players WHERE name=:name ''', {"name": name})
        self.conn.commit()

    def get_profile(self, name):
        self.c.execute('''SELECT * FROM players WHERE name=:name''', {"name": name})
        return self.c.fetchall()

    # Matches database methods
    def add_match(self):
        return

    def remove_match(self):
        return

    def get_player_matches(self):
        return

    def get_pvp_matches(self):
        return

    def get_all_matches(self):
        return


class Logger(object):
    def __init__(self):
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(Levelname)s:%(name)s: %(message)s'))


class Bot(object):
    def __init__(self):
        self.client = discord.Client()
        self.token = ''
        self.prefix = '!'
        self.log = Logger()
        self.db = Database()
        self.active_matches = {}

        @self.client.event
        async def on_ready():
            print('We have logged in as {0.user}'.format(self.client))

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            if message.content.startswith(self.prefix):
                command = message.content.strip(self.prefix).split()
                if not command:
                    return

                if command[0] == 'register':
                    await self.register(message)
                elif command[0] == 'unregister':
                    await self.unregister(message)
                elif command[0] == 'profile':
                    await self.profile(message)
                elif command[0] == 'rules':
                    await self.rules(self, message)
                elif command[0] == 'challenge':
                    await self.challenge(message, command[1])
                elif command[0] == 'winner':
                    await self.results(message, command[1])
                else:
                    await self.error(message, "Unknown command.")

        self.client.run(self.token)

    async def register(self, message):
        name = message.author.mention
        if self.db.player_exists(name):
            await self.error(message, name + " is already registered.")
            return
        self.db.add_player(name)
        await self.send_message(message=message,
                                title='Registration',
                                description=name + ' registered successfully.',
                                msg_type='success')

    async def unregister(self, message):
        name = message.author.mention
        if not self.db.player_exists(name):
            await self.error(message, name + " is not registered.")
            return
        self.db.remove_player(name)
        await self.send_message(message=message,
                                title='Unregistration',
                                description=name + ' unregistered successfully.',
                                msg_type='success')

    async def profile(self, message):
        name = message.author.mention
        results = self.db.get_profile(name)

        if not results:
            await self.error(message, "Profile not found.")
            return

        await self.send_message(message=message,
                                title=message.author.name + "'s Profile",
                                description='```' +
                                            'Role:   ' + str(results[0][5]) + '\n' +
                                            'Points: ' + str(results[0][1]) + '\n' +
                                            'Wins:   ' + str(results[0][2]) + '\n' +
                                            'Losses: ' + str(results[0][3]) + '\n' +
                                            'Draws:  ' + str(results[0][4]) + '```',
                                msg_type='info')

    @staticmethod
    async def rules(self, message):
        await self.send_message(message=message,
                                title='Standard Rules',
                                description='```Map:    Battle Arena' + '\n' +
                                            'Rounds: 20' + '\n' +
                                            'HP/AP:  100/50' + '\n' +
                                            'Damage: 15 or less```' + '\n',
                                msg_type='info')

    async def challenge(self, message, challenged):
        # TODO: create match
        challenger = message.author.mention
        challenged = challenged
        # issue challenge message
        await self.send_message(message=message,
                                title='Challenge Issued',
                                description=
                                challenger + " has challenged " + challenged + '\n\n' +
                                "Type `!accept` " + challenger + " or !decline " + challenger +
                                ' to respond.'
                                ,
                                msg_type='info')
        # wait for response

        def check(m):
            # TODO: translate input to @mention
            print(message.author.mention)
            print(challenged)
            if message.author.mention == challenged and message.content == '!accept' + challenged:
                return True
            elif message.author.mention == challenged and message.content == '!decline' + challenged:
                return True
            else:
                return False

        msg = await self.client.wait_for('message', check=check, timeout=30)
        print(msg)
        return

    async def results(self, message, winner):
        # TODO: create results
        # issue results message
        # record match to database
        return

    async def error(self, message, error_message):
        await self.send_message(message=message,
                                title='Error',
                                description=error_message,
                                msg_type='error')

    async def send_message(self, message, title, description, msg_type):
        if msg_type == 'battle':
            thumbnail = 'https://images.emojiterra.com/twitter/v13.0/512px/2694.png'
        elif msg_type == 'success':
            thumbnail = 'https://images.emojiterra.com/google/android-10/128px/2705.png'
        elif msg_type == 'info':
            thumbnail = 'https://images.emojiterra.com/google/android-10/128px/1f4dc.png'
        else:
            thumbnail = 'https://pbs.twimg.com/profile_images/378800000460921795/b8465af947492fc6a565a57da0535bfe.jpeg'
        output = discord.Embed(title=title,
                               description=description,
                               timestamp=datetime.now())
        output.set_thumbnail(url=thumbnail)
        await message.channel.send(embed=output)


def main():
    Bot()


if __name__ == "__main__":
    main()
