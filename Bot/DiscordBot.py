import atexit
import os
import pickle
import signal

import discord

from Bot.Cogs.InfoCog import InfoCog
from Bot.Cogs.TeamCog import TeamCog


class DiscordBot(discord.Bot):
    def __init__(self, load_config=False, **options):
        self.load_config = load_config
        self.cog = None
        if __name__ == '__main__':
            signal.signal(signal.SIGINT, lambda sig,frame: self.on_disconnect()) # ctlr + c

        super().__init__(**options)

        self.cog = TeamCog(self)
        self.add_cog(self.cog)
        self.add_cog(InfoCog(self))

        self.load_extension('Bot.Cogs.InfoCog')
        self.load_extension('Bot.Cogs.TeamCog')

    # event that runs when the bot is started
    async def on_ready(self):
        print(f'{self.user} ready!')

        # if config file exists and bot is set to use stored information, load config file
        if self.load_config and os.path.exists('TeamData.obj'):
            with open('TeamData.obj', 'rb') as f:
                team_manager = pickle.load(f)
                self.cog.set_team_manager(team_manager)

        atexit.register(self.on_disconnect)

    # callback before the bot exits (stores the current team manager data)
    def on_disconnect(self):
        with open('TeamData.obj', 'wb') as f:
            pickle.dump(self.cog.get_team_manager(), f)
