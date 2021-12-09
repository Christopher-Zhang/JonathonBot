import discord


#############
### NAMES ###
#############
SANTA_FILE_NAME = 'santa'
# BOT_PREFIX = 'p!'


#############
### LINKS ###
#############
SANTA_ICON_URL = "https://i.imgur.com/ZMsF3Yt.png"
HELP_ICON_URL = "https://clipart.world/wp-content/uploads/2020/06/Question-Mark-clipart-transparent.png"




#################
### RESPONSES ###
#################
santa_help_alert = discord.Embed(
    title = "Here are some commands to help you get started!",
    description = ("You can just DM me the following commands, no prefix needed!\n\n\n" +
        "**info**\n- Use this command to see the relevant info about your Secret Santa gift exchanges!\n\n"
        "**message [insert cheery words here]**\n- Give your Secret Santa a message, respond to their questions!\n\n" +
        '**request [address, wishlist, christmas]**\n- Use this command to anonymously request information from your Secret Santee™, type "request" to see more details')
)
santa_help_alert.set_thumbnail(url=HELP_ICON_URL)

santa_start_alert = discord.Embed(
    title = (":christmas_tree::christmas_tree: MATCHUPS HAVE BEEN DRAWN! :christmas_tree::christmas_tree:"),
    description = "Please check your DMs to see your Secret Santee™!"
)
santa_start_alert.set_thumbnail(url=SANTA_ICON_URL)

santa_no_exchange_response = "You are not a part of any Secret Santa gift exchanges!"

def not_created_message(guild: discord.Guild):
     return "There is no Secret Santa for **" + guild.name + "** yet!"