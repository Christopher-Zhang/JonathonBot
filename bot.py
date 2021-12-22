import discord
from pretty_help import PrettyHelp, DefaultMenu
import os
import santa
import config
# import money
# from constants import santa_constants as santac
from pymongo import MongoClient
from constants import names
from dotenv import load_dotenv
from discord.ext import commands

### bot setup
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.members = True
menu = DefaultMenu(":arrow_left:",":arrow_right",":white_check_mark:")
bot = commands.Bot(
    command_prefix=names.BOT_PREFIX, 
    intents=intents,
    help_command=PrettyHelp(
        navigation = menu,
        color = discord.Colour.red()
        # show_index = False
    )
)
mongo_url = os.getenv('MONGODB_URL')
mongo_client = MongoClient(mongo_url)
bot.add_cog(santa.Santa(bot))
bot.add_cog(config.Config(bot))
# bot.add_cog(money.Money(bot, mongo_client))

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord")
    print("I am a part of: ")
    for guild in bot.guilds:
        print("**" + guild.name + "**")

bot.run(DISCORD_TOKEN)