import sys
import discord
import json
import os
import embed_creator
import urllib
from bs4 import BeautifulSoup

# Basic Command Handler
async def handle_command(client, message, user_priority):
    
    # Split Command Into Components And Remove Prefix
    command = message.content[1:].lower().split(" ")
    
    # Default To Unknown Command
    function = globals()["unknown_command"]
    
    # If Command Is In botcommands.json, Set function To The Corresponding Method
    for c in command_list["commands"]:
        if(c["name"].lower() == command[0]):
            # Check User's Priority Level
            if(c["level"] <= user_priority):
                try:
                    function = globals()[command[0]]
                except Exception:
                    # In This Case, The Command Is In botcommands.json But Isn't A Method
                    await message.channel.send(embed = embed_creator.create_embed("Command Unavailable", "This command is under maintenece or coming soon.", discord.Color.dark_red()))
                    pass
            # User Doesn't Have Access
            else:
                function = globals()["access_denied"]
    
    # Call The Command Function
    await function(client, message, user_priority)

# ACCESS DENIED
async def access_denied(client, message, user_priority):
    
    await message.channel.send(embed = embed_creator.create_embed("Access Denied", "You don't have permission to use this command.", discord.Color.dark_red()))

# UNKNOWN COMMAND
async def unknown_command(client, message, user_priority):
    
    await message.channel.send(embed = embed_creator.create_embed("Unknown Command", "The command you've entered is invalid.", discord.Color.dark_red()))

# INCORRECT USAGE
async def incorrect_usage(client, message, user_priority):
    
    # Split Command Into Components And Remove Prefix
    command = message.content[1:].lower().split(" ")
    
    for c in command_list["commands"]:
        if (c["name"].lower() == command[0]):
            await message.channel.send(embed = embed_creator.create_embed("Incorrect Usage", "Usage : {}".format(c["usage"]), discord.Color.dark_red()))
    
# PING
async def ping(client, message, user_priority):
    
    # Pong!
    await message.channel.send(embed = embed_creator.create_embed("Pong!", "", discord.Color.dark_red()))

# ECHO
async def echo(client, message, user_priority):
    try:
        # Echo Whatever Comes After The Echo Command
        await message.channel.send(embed = embed_creator.create_embed(" ".join(message.content.split(" ")[1:]), "", discord.Color.dark_red()))
    except Exception:
        await incorrect_usage(client, message, user_priority)
    
# HELP
async def help(client, message, user_priority):
    
    # Create Empty String
    command_list_str = ""
    
    # Add Commands To The String
    for c in command_list["commands"]:
        if(c["level"] <= user_priority):
            command_list_str += c["name"] + " : " + c["desc"] + "\n"
    
    await message.channel.send(embed = embed_creator.create_embed("List of Commands", command_list_str, discord.Color.dark_red()))

async def opgg(client, message, user_priority):
    
    try:
        # Remove Prefix and opgg
        names = message.content.split(" ")[1:]
        names = " ".join(names)
        names = names.split(" has joined the lobby.")
        
        for name in names:
            if name == "":
                names.remove(name)
        
        for name_str in names:
            
            # Request HTML
            player_url = "https://na.op.gg/summoner/userName={}".format(name_str.replace(" ", "_"))
            req = urllib.request.Request(player_url)
            
            with urllib.request.urlopen(req) as response:
                
                # Create Soup Object
                html = response.read()
                soup = BeautifulSoup(html, "html.parser")
                
                try:
                    
                    # Get Icon URL
                    icon_url = "https:" + str(soup.find_all(class_="ProfileImage")[0]).split("\"")[3]
                    try:
                        rank = str(soup.find_all(class_="TierRank")[0]).split(">")[1].split("<")[0] + " " + str(soup.find_all(class_="LeaguePoints")[0]).split(">")[1].split("<")[0].replace("	", "").replace("\n", "") + " (" + str(soup.find_all(class_="WinRatio")[0]).split(">")[1].split("<")[0].replace("	", "").replace("\n", "") + ")"
                    except Exception:
                        rank = "Unranked"
                    
                    # Get Riot ID
                    player_name = str(soup.find_all(class_="Name")[0]).split(">")[1].split("<")[0]
                    
                    # Get Most Played Champs
                    most_played = "**Most Played Champions:**"
                    champs = soup.find_all(class_="ChampionBox Ranked")
                    
                    # Show Most Played Champions
                    if(len(champs) > 5):
                        champs = champs[:5]
                    else:
                        champs = champs[:len(champs)]
                    
                    # Add Champion, Games, and Winrate % To Description
                    for box in champs:
                        
                        champ_name = str(box).split("alt=\"")[1].split("\"")[0]
                        games_played = str(box).split("class=\"Title\">")[1].split("</div>")[0].replace("	", "").replace("\n", "")
                        winrate = str(box).split("title=\"Win Ratio\">")[1].split("</div>")[0].replace("	", "").replace("\n", "")
                        
                        most_played += f"\n{champ_name}: {winrate} *({games_played})*"
                    
                    # Show W/L For Last 10 Games Played
                    recent_games = ""
                    games = soup.find_all(class_="GameResult")
                    
                    if(len(games) > 10):
                        games = games[:10]
                    else:
                        games = games[:len(games)]
                    
                    # Add Win/Loss To A New Field
                    for box in games:
                        
                        if "Defeat" in (str(box).split("	")):
                            recent_games += f":red_circle:"
                        else:
                            recent_games += f":blue_circle:"
                    
                    if(recent_games == ""):
                        recent_games = "*No Recent Games.*"
                    
                    # Compile Embed
                    profile_embed = embed_creator.create_embed(rank, most_played, discord.Color.blue())
                    profile_embed.set_author(name = player_name, url = player_url, icon_url = icon_url)
                    profile_embed.add_field(name = "*Recent Games:*", value = recent_games, inline = False)
                    
                except Exception:
                    
                    # Profile Not Found
                    profile_embed = embed_creator.create_embed("{}".format(" ".join(name_str)), "Profile Not Found.", discord.Color.blue())
                
                await message.channel.send(embed = profile_embed)
                
    except Exception:
        await incorrect_usage(client, message, user_priority)

# PURGE

async def purge(client, message, user_priority):
    
    try:
        
        #Get Number Of Messages To Purge
        command = message.content.split(" ")
        await message.channel.purge(limit = int(command[1]) + 1)
        await message.channel.send(embed = embed_creator.create_embed("Messages Cleared", f"{message.author.mention} cleared {command[1]} messages.", discord.Color.dark_red()))
    
    except Exception:
        await incorrect_usage(client, message, user_priority)

# DISCONNECT
async def disconnect(client, message, user_priority):
    
    # Send Disconnect Message & Disconnect
    await message.channel.send(embed = embed_creator.create_embed("Disconnecting", "", discord.Color.dark_red()))
    await client.logout()

# INFO
async def info(client, message, user_priority):
    
    # If Channel Is A DM, Send Bot Info
    if message.channel.type is discord.ChannelType.private:
        await message.channel.send(embed = embed_creator.create_embed("Bot Info", f"Token : {sys.argv[1]}\nCommand Prefix : {sys.argv[2]}", discord.Color.dark_red()))
    # Otherwise, Tell The User To DM Instead
    else:
        await message.channel.send(embed = embed_creator.create_embed("Improper Channel", "This command cannot be used in a server.", discord.Color.dark_red()))

# LIST SERVERS
async def listservers(client, message, user_priority):
    
    guilds_str = ""
    guilds = client.guilds
    for guild in guilds:
        guilds_str += guild.name + "\n"
    
    await message.channel.send(embed = embed_creator.create_embed("List of Servers:", guilds_str, discord.Color.dark_red()))

# ANNOUNCE
async def announce(client, message, user_priority):
    
    try:
        author = f"{message.author.name}#{message.author.discriminator}"
        author_pfp = message.author.avatar_url
        
        fields = []
        announcement_str = " ".join(message.content.split(" ")[1:])
        announcement_fields = announcement_str.split("\n")
        
        for field in announcement_fields:
            
            fields.append(field.split(" : "))
        
        
        guilds = client.guilds
        for guild in guilds:
            for channel in guild.channels:
                if((channel.type == discord.ChannelType.text) & (channel.name == "bot_announcements")):
                    announcement_embed = embed_creator.create_embed(fields[0][0], fields[0][1], discord.Color.dark_red())
                    fields.remove(fields[0])
                    announcement_embed.set_author(name = author, icon_url = author_pfp)
                    for field in fields:
                        announcement_embed.add_field(name = field[0], value = field[1], inline = False)
                    
                    await channel.send(embed = announcement_embed)
        
        await message.channel.send(embed = embed_creator.create_embed("Success", "Announcement Sent Successfully", discord.Color.dark_red()))
    
    except Exception:
        await incorrect_usage(client, message, user_priority)
        
# Load Commands
command_list = json.load(open(os.path.join(os.path.dirname(__file__), "./botcommands.json")))