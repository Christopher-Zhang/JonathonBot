import os
import discord

from dotenv import load_dotenv
from pymongo import MongoClient
from discord.ext import commands
from constants import money_constants as mc

class Money(
    commands.Cog,
    name = "Money",
    description = "For making bad financial decisions"
):

    def __init__(self, bot: commands.Bot, mongo_client: MongoClient):
        self.bot = bot
        self._last_member = None
        self.mongo_client = mongo_client

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        
        if not message.guild:
            pass
    
    @commands.command(
        aliases = ['g', 'Gamble', 'G']
    )
    async def gamble(self, ctx: commands.Context, *args):
        if len(args) < 1:
            response = mc.MISSING_ARGS_RESPONSE
        else:
            wager = args[0]
            current_balance = await fetch_balance(ctx.author.id)


async def fetch_balance(self, user_id: int):
    # balance = self.mongo_client
    balance = 0
    return balance

