import discord
import random
import os

from discord.ext.commands.core import check
from util import utils
from constants import santa_constants as santac
from discord.ext import commands


class Santa(
    commands.Cog,
    name = "Santa",
    description = "For Secret Santa Gift Exchange"#,
    # help = "For Secret Santa gift exchange, commands include:\n\njoin, info, leave"
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if not message.guild:
            try:
                author = message.author
                content = message.content
                if message.content.startswith('info'):
                    await handle_dm_info(message, self.bot.guilds)
                elif content.startswith('request'):
                    await handle_dm_request(message, self.bot.guilds)
                elif content.startswith('message'):
                    await handle_dm_message(message, self.bot.guilds)
                elif content.startswith('help'):
                    await author.send(embed=santac.santa_help_alert)
                else:
                    await author.send('Type "help" to get started!')
            except discord.errors.Forbidden:
                pass
        else:
            pass
            # await self.bot.process_commands(message)
    @commands.command(
        aliases = ["s", "ss"],
        description = "For Secret Santa Gift Exchange!",
        help = "join, info, leave"
    )
    async def santa(self, ctx: commands.Context, *args):
        send_response = True
        if not args:
            return
        elif args[0] == "join":
            response = await handle_command_join(ctx)
        elif args[0] == "create":
            response = await handle_command_create(ctx)
        elif args[0] == "start":
            response = await handle_command_start(ctx)
            send_response = False
        elif args[0] == "set_budget":
            response = handle_command_set_budget(ctx, args[1:])
        elif args[0] == "leave":
            response = await handle_command_leave(ctx)
        elif args[0] == "info":
            response = handle_command_info(ctx)
        elif args[0] == 'delete':
            response = await handle_command_delete(ctx)
        else:
            send_response = False
        if send_response:
            await ctx.channel.send(response)


async def handle_dm_info(message: discord.Message, guilds: list):
    author = message.author
    exists = False
    for guild in guilds:
        print(guild.name)
        if await guild.fetch_member(author.id):
            file_name = get_file_name(guild.id)
            if os.path.exists(file_name):
                exists = True
                santa_data = read_santa_data(guild.id)
                santee = santa_data["matchups"][str(author.id)]
                embed = discord.Embed(
                    title = "Secret Santa for " + santa_data["server_name"],
                    description = (
                        "Budget: **$" + str(santa_data["budget"]) + "**\n\n" + "Your Secret Santee™ : **" + santa_data["id_to_name"][str(santee)] + "**" if santa_data["matched"] 
                            else "Budget: $" + str(santa_data["budget"])
                    )
                )
                embed.set_thumbnail(url=santac.SANTA_ICON_URL)
                message = await author.send(embed=embed)
    if not exists:
        await author.send(santac.santa_no_exchange_response)

async def handle_dm_request(message: discord.Message, guilds: list):
    content = message.content
    author = message.author
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
        for guild in guilds:
            if await guild.fetch_member(author.id):
                file_name = get_file_name(guild.id)
                if check_santa_data(guild.id):
                    exists = True
                    santa_data = read_santa_data(guild.id)
                    embed = discord.Embed(
                        title = "A Message From Your Secret Santa!",
                        description = message,
                    )
                    embed.set_thumbnail(url=santac.SANTA_ICON_URL)
                    success = False
                    try:
                        santee = await guild.fetch_member(santa_data["matchups"][str(author.id)])
                        await santee.send(embed=embed)
                        success = True
                    except:
                        pass
                    response = "Request sent successfully!" if success else "Failed to send message..."
        if not exists:
            response = santac.santa_no_exchange_response
    else:
        response = ("To protect the sanctity of this blessed holiday ritual, you may choose from these options three:\n" + 
            "address - if you need their shipping address\nwishlist - if you need some help choosing\n" +
            "christmas - if you just want to wish your Secret Santee™ a Merry Christmas\n\n" +
            "Example: request address")
    await author.send(response)

async def handle_dm_message(message: discord.Message, guilds: list):
    content = message.content
    author = message.author
    original_message = content[8:]
    embed = discord.Embed(
        title = "Your Secret Santee™ **" + author.name + "** is sending you the following message!  ",
        description = original_message
    )
    embed.set_thumbnail(url=santac.SANTA_ICON_URL)
    # TODO let user pick which secret santa to send to
    # response = "Pick out of the following servers:"
    exists = False
    success = False
    for guild in guilds:
        print(guild.name)
        if await guild.fetch_member(author.id):
            # file_name = get_file_name(guild.id)
            if check_santa_data(guild.id):
                santa_data = read_santa_data(guild.id)
                exists = True
                try:
                    recipient = await guild.fetch_member(santa_data["matchups"][str(author.id)])
                    await recipient.send(embed=embed)
                    success = True
                except discord.errors.Forbidden:
                    pass
    if not exists:
        response = santac.santa_no_exchange_response
    else:
        if success:
            response = "Message successfully sent!"
        else:
            response = "Failed to send message..."
    await author.send(response)

async def handle_command_join(ctx: commands.Context):
    santa_data = read_santa_data(ctx.guild.id)
    if santa_data:
        id_ = ctx.author.id
        name_ = ctx.author.name
        if id_ in santa_data["participants"]:
            response = "You are already registered for the Secret Santa gift exchange" + f"{ctx.author.mention}!"
        else:
            santa_data["participants"].append(id_)
            santa_data["name_to_id"][name_] = id_
            santa_data["id_to_name"][id_] = name_
            role = ctx.guild.get_role(santa_data["role_id"])
            if(role == None):
                print("Santa role not found")
                #TODO make better logs
            else:
                await ctx.author.add_roles(role, reason = "Joined Secret Santa")
            response = "Welcome to the **" + ctx.guild.name + "** Secret Santa gift exchange" + f"{ctx.author.mention}!"
    else:
        response = santac.not_created_message(ctx.guild)
    write_santa_data(ctx.guild.id, santa_data)
    return response

async def handle_command_create(ctx: commands.Context):
    # permissions_ = user_.guild_permissions
    # if permissions_.administrator:
    id_ = ctx.author.id
    santa_data = None
    if id_ == 140967651701817345:
        if check_santa_data(ctx.guild.id):
            response = "There is already a Secret Santa for **" + ctx.guild.name + "**"
        else:
            role = await create_santa_role(ctx.guild)
            santa_data = {
                "participants": [],
                "matchups": {},
                "matchups_r": {},
                "server_id": ctx.guild.id,
                "server_name": ctx.guild.name,
                "name_to_id": {},
                "id_to_name": {},
                "budget": 0,
                "matched": False,
                "role_id": role.id
            }
            response = "Successfully created a Secret Santa gift exchange for **" + ctx.guild.name + "**"
    else:
        response = "You are too weak to create a Secret Santa"
    if santa_data:
        write_santa_data(ctx.guild.id, santa_data)
    return response

async def handle_command_start(ctx: commands.Context):
    # permissions_ = user_.guild_permissions
    # if permissions_.administrator:
    id_ = ctx.author.id
    santa_data = read_santa_data(ctx.guild.id)
    if id_ == 140967651701817345: # hardcode for me
        # response = ":christmas_tree::confetti_ball: SECRET SANTA GIFT EXCHANGE MATCHUPS HAVE BEEN DRAWN, PLEASE CHECK YOUR DMs TO FIND OUT YOUR SECRET SANTEE! :confetti_ball::christmas_tree:"
        santa_data = await create_matchups(ctx, santa_data)
        write_santa_data(ctx.guild.id, santa_data)
        await ctx.channel.send(embed=santac.santa_start_alert)
        response = None
    else:
        response = "You are too weak to start this Secret Santa"
    return response
def handle_command_set_budget(ctx: commands.Context, args: list):
    santa_data = read_santa_data(ctx.guild.id)
    id_ = ctx.author.id
    if not santa_data:
        response = santac.not_created_message(ctx.guild)
    elif len(args) < 1:
        response = "Please give a value"
    else:
        # permissions_ = user_.guild_permissions
        # if permissions_.administrator:
        if id_ == 140967651701817345:
            val = int(args[0])
            santa_data["budget"] = val
            response = "Successfully set the budget to **$" + str(val) + "**"
        else:
            response = "You are too weak to edit this Secret Santa"
    write_santa_data(ctx.guild.id, santa_data)
    return response

async def handle_command_leave(ctx: commands.Context):
    santa_data = read_santa_data(ctx.guild.id)
    id_ = ctx.author.id
    if not santa_data:
        response = santac.not_created_message
    else:
        if id_ not in santa_data["participants"]:
            response = santac.santa_no_exchange_response
        elif santa_data["matched"]:
            response = "Its too late! Matchups have already been drawn!"
        else:
            santa_data["participants"].remove(id_)
            role = ctx.guild.get_role(santa_data["role_id"])
            await ctx.author.remove_roles(role, reason = "Member left Secret Santa")
            response = "You have been successfully removed from this server's Secret Santa gift exchange!"
    write_santa_data(ctx.guild.id, santa_data)
    return response

def handle_command_info(ctx: commands.Context):
    santa_data = read_santa_data(ctx.guild.id)
    if not santa_data:
        response = santac.not_created_message(ctx.guild)
    else:
        ids = santa_data["participants"]
        # random.shuffle(ids)
        name_dict = santa_data["id_to_name"]
        response = "Here is a list of the current participants:"
        for id in ids:
            name = name_dict[str(id)]
            response += "\n**" + name + "**"
        response += "\n\nThe current budget is: **$" + str(santa_data["budget"]) + "**"
    return response

async def handle_command_delete(ctx: commands.Context):
    id_ = ctx.author.id
    file_name = get_file_name(ctx.guild.id)
    if check_santa_data(ctx.guild.id):
        if id_ == 140967651701817345:
            santa_data = read_santa_data(ctx.guild.id)
            if santa_data and "role_id" in santa_data:
                role = ctx.guild.get_role(santa_data["role_id"])
                await role.delete(reason = 'Deleting current Secret Santa')
            os.remove(file_name)
            response = "Successfully deleted this server's Secret Santa"
        else:
            response = "You are too weak to delete this Secret Santa"
    else:
        response = "There is no existing Secret Santa for this server"
    return response

### helpers

async def create_santa_role(guild: discord.Guild):
    role = await guild.create_role(
        name = 'Santa Gamer',
        colour = discord.Colour.dark_green(),
        reason = 'For Secret Santa ID'
    )
    return role

def read_santa_data(guild_id: discord.Guild.id):
    file_name = get_file_name(guild_id)
    try:
        return utils.read_from_file(file_name)
    except:
        os.remove(file_name)
        print("Error in file, deleting...")
        return
def write_santa_data(guild_id: discord.Guild.id, santa_data: dict):
    file_name = get_file_name(guild_id)
    utils.write_to_file(santa_data, file_name)

def check_santa_data(guild_id: discord.Guild.id):
    file_name = get_file_name(guild_id)
    return os.path.exists(file_name)

def get_file_name(guild_id: discord.Guild.id):
    file_name = santac.SANTA_FILE_NAME + "_" + str(guild_id) + ".txt"
    return file_name
async def create_matchups(ctx: commands.Context, santa_data: dict):
    player_list = santa_data["participants"]
    length = len(player_list)
    if length < 2:
        return santa_data
    random_list1 = player_list.copy()
    random.shuffle(random_list1)
    random_list2 = random_list1.copy()
    n = random.randint(1,length-1)
    ## make sure it is not just a 1v1
    # while n == length/2 and length != 2:
    #     n = random.randint(0, length)
    random_list2 = utils.rotate_list(random_list2, n)
    matchups = {}
    matchups_r = {}
    members = []
    for i in range(length):
        id = random_list1[i]
        matchups[str(id)] = random_list2[i]
        matchups_r[str(random_list2[i])] = id
        member = await ctx.guild.fetch_member(id) 
        members.append(member)
    santa_data["matchups"] = matchups
    santa_data["matchups_r"] = matchups_r
    santa_data["matched"] = True
    # alert participants
    for i in range(length):
        member = members[i]
        recipient_id = matchups[str(member.id)]
        # message = "**" + member.name + "**, you are the Secret Santa for **" + id2name[recipient_id] + "**. Be good to them!"
        pairing_alert = discord.Embed(
            title = "**" + member.name + "**! Your Secret Santa pairing has been picked!",
            description = ("Your Secret Santee™ is **" + santa_data["id_to_name"][str(recipient_id)] + "**!\n\n" +
                "Make sure to give them a great present!\n\nThis Secret Santa gift exchange's budget is currently set to **$" + 
                str(santa_data["budget"]) + '**\n\nType **"help"** to get started!'),
            )\
            .set_thumbnail(url=santac.SANTA_ICON_URL)
        try:
            await member.send(embed=pairing_alert)
            # await member.send(embed=santac.santa_help_alert)
        except discord.errors.Forbidden:
            pass
    return santa_data
async def alert_players(message: discord.Message, members: list):
    for member in members:
        await member.send(message)