import asyncio

import discord


# a subclass of the pycord View which is deleted after a fixed amount of seconds
class TemporaryView(discord.ui.View):
    def __init__(self, timeout: int, timeout_function: callable):
        self.timeout = timeout
        self.timeout_function = timeout_function
        asyncio.create_task(self.timeout_func())

    async def timeout_func(self):
        await asyncio.sleep(self.timeout)
        self.timeout_function()
        self.disable_all_items()