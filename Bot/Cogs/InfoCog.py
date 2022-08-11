import discord

from Bot.Embeds.InfoEmbed import InfoEmbed


class InfoCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    # event that runs when the "info" command is sent
    @discord.application_command()
    async def info(self, ctx):
        await ctx.respond(embed=InfoEmbed())
