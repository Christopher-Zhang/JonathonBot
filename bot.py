import discord
import random
import os
from utils import *
from dotenv import load_dotenv
from discord.ext import commands


# bot setup
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SANTA_FILE_NAME = os.getenv('SANTA_FILE_NAME')
SANTA_ICON_URL = "https://i.imgur.com/ZMsF3Yt.png"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="j!")

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord")
    print("I am a part of: ")
    for guild in bot.guilds:
        print(guild.name)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if not message.guild:
        try:
            author = message.author
            content = message.content
            if content.startswith('info'):
                exists = False
                guilds = bot.guilds
                for guild in guilds:
                    print(guild.name)
                    if await guild.fetch_member(author.id):
                        file_name = SANTA_FILE_NAME + "_" + str(guild.id) + ".txt"
                        if os.path.exists(file_name):
                            exists = True
                            santa_data = read_from_file(file_name)
                            santee = santa_data["matchups"][str(author.id)]
                            embed = discord.Embed(
                                title = "Secret Santa for " + santa_data["server_name"],
                                description = (
                                    "Budget: " + str(santa_data["budget"]) + "\n" + "Your Secret Santee™ : **" + santa_data["id_to_name"][str(santee)] + "**" if santa_data["matched"] 
                                        else "Budget: $" + str(santa_data["budget"])
                                )
                            )
                            embed.set_thumbnail(url=SANTA_ICON_URL)
                            message = await author.send(embed=embed)
                            # await bot.add_reaction(message, )
                if not exists:
                    await author.send("You are not a part of any Secret Santas")
            elif content.startswith('request'):
                args = content[8:]
                valid = True
                message = ''
                if args.lower() == "address":
                    message = "Your Secret Santa is requesting your shipping address.\n\nDoxx yourself: message [message contents]"
                elif args.lower() == "wishlist":
                    message = "Your Secret Santa needs help choosing a gift smh...\n\nHelp them out: message [message contents]"
                elif args.lower() == "christmas":
                    message = "Your Secret Santa wishes you a Merry Christmas!\n\nReturn the favor: message [message contents]"
                else:
                    valid = False
                if valid:
                    exists = False
                    guilds = bot.guilds
                    for guild in guilds:
                        if await guild.fetch_member(author.id):
                            file_name = SANTA_FILE_NAME + "_" + str(guild.id) + ".txt"
                            if os.path.exists(file_name):
                                exists = True
                                santa_data = read_from_file(file_name)
                                embed = discord.Embed(
                                    title = "A Message From Your Secret Santa!",
                                    description = message,
                                )
                                embed.set_thumbnail(url=SANTA_ICON_URL)
                                success = False
                                try:
                                    santee = await guild.fetch_member(santa_data["matchups"][str(author.id)])
                                    await santee.send(embed=embed)
                                    success = True
                                except:
                                    pass
                                response = "Successfully sent message!" if success else "Failed to send message..."
                    if not exists:
                        response = "You are not a part of any Secret Santas..."
                        
                else:
                    response = ("To protect the sanctity of this blessed holiday ritual, you may choose from these options three:\n" + 
                        "address - if you need their shipping address\nwishlist - if you need some help choosing\n" +
                        "christmas - if you just want to wish your Secret Santee™ a Merry Christmas\n\n" +
                        "Example: request address")
                await author.send(response)
            elif content.startswith('message'):
                original_message = content[8:]
                embed = discord.Embed(
                    title = "Your Secret Santee™ **" + author.name + "** is sending you the following message!  ",
                    description = original_message

                )
                embed.set_thumbnail(url=SANTA_ICON_URL)
                # TODO let user pick which secret santa to send to
                # response = "Pick out of the following servers:"
                exists = False
                success = False
                guilds = bot.guilds
                for guild in guilds:
                    print(guild.name)
                    if await guild.fetch_member(author.id):
                        file_name = SANTA_FILE_NAME + "_" + str(guild.id) + ".txt"
                        if os.path.exists(file_name):
                            santa_data = read_from_file(file_name)
                            exists = True
                            try:
                                recipient = await guild.fetch_member(santa_data["matchups"][str(author.id)])
                                await recipient.send(embed=embed)
                                success = True
                            except:
                                pass
                if not exists:
                    response = "You are not a part of any Secret Santas..."
                else:
                    if success:
                        response = "Message successfully sent!"
                    else:
                        response = "Failed to send message..."
                await author.send(response)
            else:
                embed = discord.Embed(
                    title = "Here is a List of the Valid Commands!",
                    description = ("No prefix needed in DMs\n\nmessage [message contents] - you can message your Secret Santa\n" +
                        "request - you can request information from your Secret Santee™\ninfo - check your Secret Santee™ and the budget")
                )
                embed.set_thumbnail(url=SANTA_ICON_URL)
                await author.send(embed=embed)
        except discord.errors.Forbidden:
            pass
    else:
        await bot.process_commands(message)

@bot.command(
    name = "santa",
    help = "join"
)
async def santa(ctx, *args):
    try:
        santa_data = read_from_file(SANTA_FILE_NAME + "_" + str(ctx.guild.id) + ".txt")
    except:
        os.remove(SANTA_FILE_NAME + "_" + str(ctx.guild.id) + ".txt")
        santa_data = None
    user_ = ctx.author
    name_ = user_.name
    id_ = user_.id
    not_created_message = "There is no Secret Santa for **" + ctx.guild.name + "** yet!"
    if not args:
        return
    elif args[0] == "join":
        if santa_data:
            if id_ in santa_data["participants"]:
                response = "You are already registered for the Secret Santa **" + name_ +  "**"
            else:
                santa_data["participants"].append(id_)
                response = "Welcome to the **" + ctx.guild.name + "** Secret Santa **" + name_ + "**"
        else:
            response = not_created_message 

    elif args[0] == "create":
        # permissions_ = user_.guild_permissions
        # if permissions_.administrator:
        if id_ == 140967651701817345:
            santa_data = {
                "participants": [],
                "matchups": {},
                "matchups_r": {},
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "name_to_id": {},
                "id_to_name": {},
                "budget": 0,
                "matched": False
            }
            response = "Successfully created a Secret Santa for **" + ctx.guild.name + "**"
        else:
            response = "You are too weak to create a secret santa"
    
    elif args[0] == "start":
        # permissions_ = user_.guild_permissions
        # if permissions_.administrator:
        if id_ == 140967651701817345:
            response = "Started"
            santa_data = await create_matchups(ctx, santa_data)
        else:
            response = "You are too weak to start this secret santa"

    elif args[0] == "set_budget":
        if not santa_data:
            response = not_created_message 
        if len(args) < 2:
            response = "Please give a value"
        else:
            # permissions_ = user_.guild_permissions
            # if permissions_.administrator:
            if id_ == 140967651701817345:
                val = int(args[1])
                santa_data["budget"] = val
                response = "Successfully set the budget to **" + val
            else:
                response = "You are too weak to edit this Secret Santa"
            
            

        
    await ctx.channel.send(response)
    print(santa_data)
    write_to_file(santa_data, SANTA_FILE_NAME + "_" + str(ctx.guild.id) + ".txt")
    return
    

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#     if message.content.startswith('j!'):
#         handle_command(message)


# def handle_command(message):
#     return

async def create_matchups(ctx, santa_data):
    player_list = santa_data["participants"]
    length = len(player_list)
    random_list1 = player_list.copy()
    random.shuffle(random_list1)
    random_list2 = random_list1.copy()
    n = random.randint(1,length-1)
    while n == length/2 and length != 2:
        n = random.randint(0, length)
        
    random_list2 = rotate_list(random_list2, n)
    matchups = {}
    matchups_r = {}
    name2id = {}
    id2name = {}
    members = []
    for i in range(length):
        id = random_list1[i]
        matchups[id] = random_list2[i]
        matchups_r[random_list2[i]] = id
        member = await ctx.guild.fetch_member(id) 
        name = member.name
        name2id[name] = id
        id2name[id] = name
        members.append(member)
    santa_data["matchups"] = matchups
    santa_data["matchups_r"] = matchups_r
    santa_data["matched"] = True
    santa_data["name_to_id"] = name2id
    santa_data["id_to_name"] = id2name
    # alert participants
    for i in range(length):
        member = members[i]
        recipient_id = matchups[member.id]
        message = "**" + member.name + "**, you are the Secret Santa for **" + id2name[recipient_id] + "**. Be good to them!"
        await member.send(message)
    return santa_data
async def alert_players(message, members):
    for member in members:
        await member.send(message)

bot.run(DISCORD_TOKEN)