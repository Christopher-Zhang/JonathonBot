import discord
import santa
from discord.ext import commands

class Config(
    commands.Cog,
    name = "Config",
    description = "Admin-type commands"
):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if not message.guild:
            ## is a dm
            pass
        else:
            ## is a server message
            pass
    
    @commands.command(
        description = "For debugging purposes",
        help = "These commands are for debugging.\nYou probably don't need to worry about them."
    )
    async def debug(self, ctx, *args):
        if args[0] == 'santa':
            if len(args) < 2:
                print("Missing arguments")
            elif args[1] == 'create_role':
                role = await santa.create_santa_role(ctx.guild)
                print('Created santa role for ' + ctx.guild.name)
                print('Name of role:', role.name)
                print('Role id: ', role.id)
        return