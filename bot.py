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
HELP_ICON_URL = "https://clipart.world/wp-content/uploads/2020/06/Question-Mark-clipart-transparent.png"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="j!")

# Globals
help_alert = discord.Embed(
    title = "Here are some commands to help you get started!",
    description = ("You can just DM me the following commands, no prefix needed!\n\n\n" +
        "**info**\n- Use this command to see the relevant info about your Secret Santa gift exchanges!\n\n"
        "**message [insert cheery words here]**\n- Give your Secret Santa a message, respond to their questions!\n\n" +
        '**request [address, wishlist, christmas]**\n- Use this command to anonymously request information from your Secret Santee™, type "request" to see more details')
)
help_alert.set_thumbnail(url=HELP_ICON_URL)
no_exchange_response = "You are not a part of any Secret Santa gift exchanges!"


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
                                    "Budget: **$" + str(santa_data["budget"]) + "**\n\n" + "Your Secret Santee™ : **" + santa_data["id_to_name"][str(santee)] + "**" if santa_data["matched"] 
                                        else "Budget: $" + str(santa_data["budget"])
                                )
                            )
                            embed.set_thumbnail(url=SANTA_ICON_URL)
                            message = await author.send(embed=embed)
                            # await bot.add_reaction(message, )
                if not exists:
                    await author.send(no_exchange_response)
            elif content.startswith('request'):
                args = content[8:]
                valid = True
                message = ''
                if args.lower() == "address":
                    message = "Your Secret Santa is requesting your shipping address.\n\nRespond using this command: message [your shipping address]"
                elif args.lower() == "wishlist":
                    message = "Your Secret Santa needs help choosing a gift smh...\n\nHelp them out with this command: message [some gift idea help]"
                elif args.lower() == "christmas":
                    message = "Your Secret Santa wishes you a Merry Christmas!\n\nReturn the favor with this command: message [some (hopefully) cheery words]"
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
                        response = no_exchange_response
                        
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
                    response = no_exchange_response
                else:
                    if success:
                        response = "Message successfully sent!"
                    else:
                        response = "Failed to send message..."
                await author.send(response)
            else:
                await author.send(embed=help_alert)
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
    valid_ = True
    user_ = ctx.author
    name_ = user_.name
    id_ = user_.id
    not_created_message = "There is no Secret Santa for **" + ctx.guild.name + "** yet!"
    if not args:
        return
    elif args[0] == "join":
        if santa_data:
            if id_ in santa_data["participants"]:
                response = "You are already registered for the Secret Santa gift exchange **" + name_ +  "**!"
            else:
                santa_data["participants"].append(id_)
                response = "Welcome to the **" + ctx.guild.name + "** Secret Santa gift exchange **" + name_ + "**!"
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
            response = "Successfully created a Secret Santa gift exchange for **" + ctx.guild.name + "**"
        else:
            response = "You are too weak to create a Secret Santa"
    
    elif args[0] == "start":
        # permissions_ = user_.guild_permissions
        # if permissions_.administrator:
        if id_ == 140967651701817345:
            start_alert = discord.Embed(
                title = (":christmas_tree::christmas_tree: MATCHUPS HAVE BEEN DRAWN! :christmas_tree::christmas_tree:"),
                description = "Please check your DMs to see your Secret Santee™!"
            )
            start_alert.set_thumbnail(url=SANTA_ICON_URL)
            # response = ":christmas_tree::confetti_ball: SECRET SANTA GIFT EXCHANGE MATCHUPS HAVE BEEN DRAWN, PLEASE CHECK YOUR DMs TO FIND OUT YOUR SECRET SANTEE! :confetti_ball::christmas_tree:"
            santa_data = await create_matchups(ctx, santa_data)
            write_to_file(santa_data, SANTA_FILE_NAME + "_" + str(ctx.guild.id) + ".txt")
            await ctx.channel.send(embed=start_alert)
        else:
            response = "You are too weak to start this Secret Santa"

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
                response = "Successfully set the budget to **$" + str(val) + "**"
            else:
                response = "You are too weak to edit this Secret Santa"

    elif args[0] == "leave":
        if not santa_data:
            response = not_created_message
        else:
            if id_ not in santa_data["participants"]:
                response = no_exchange_response
            elif santa_data["matched"]:
                response = "Its too late! Matchups have already been drawn!"
            else:
                santa_data["participants"].remove(id_)
                response = "You have been successfully removed from this server's Secret Santa gift exchange!"

    elif args[0] == "list":
        if not santa_data:
            response = not_created_message
        else:
            ids = santa_data["participants"]
            # random.shuffle(ids)
            name_dict = santa_data["id_to_name"]
            response = "Here are a list of the current participants:"
            for id in ids:
                name = name_dict[str(id)]
                response += "\n" + name
            response += "\n\nThe current budget is: **$" + str(santa_data["budget"]) + "**"
    else:
        valid = False
    if valid:
        await ctx.channel.send(response)
    # print(santa_data)
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
    # while n == length/2 and length != 2:
    #     n = random.randint(0, length)
        
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
        # message = "**" + member.name + "**, you are the Secret Santa for **" + id2name[recipient_id] + "**. Be good to them!"
        pairing_alert = discord.Embed(
            title = "**" + member.name + "**! Your Secret Santa pairing has been picked!",
            description = ("Your Secret Santee™ is **" + id2name[recipient_id] + "**!\n\n" +
                "Make sure to give them a great present!\n\nThis Secret Santa gift exchange's budget is currently set to **$" + str(santa_data["budget"]) + "**"),
        )
        pairing_alert.set_thumbnail(url=SANTA_ICON_URL)
        await member.send(embed=pairing_alert)
        await member.send(embed=help_alert)
    return santa_data
async def alert_players(message, members):
    for member in members:
        await member.send(message)

bot.run(DISCORD_TOKEN)