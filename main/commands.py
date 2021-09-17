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
    
# PING
async def ping(client, message, user_priority):
    
    # Pong!
    await message.channel.send(embed = embed_creator.create_embed("Pong!", "", discord.Color.dark_red()))

# ECHO
async def echo(client, message, user_priority):
    
    # Echo Whatever Comes After The Echo Command
    await message.channel.send(embed = embed_creator.create_embed(" ".join(message.content.split(" ")[1:]), "", discord.Color.dark_red()))
    
# HELP
async def help(client, message, user_priority):
    
    # Create Empty String
    command_list_str = ""
    
    # Add Commands To The String
    for c in command_list["commands"]:
        command_list_str += c["name"] + " : " + c["desc"] + "\n"
    
    await message.channel.send(embed = embed_creator.create_embed("List of Commands", command_list_str, discord.Color.dark_red()))

async def opgg(client, message, user_priority):
    
    command = message.content.split(" ")[1:]
    
    url = "https://na.op.gg/summoner/userName={}".format("_".join(command))
    req = urllib.request.Request(url)
    
    with urllib.request.urlopen(req) as response:
        
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        
        icon_url = "https:" + str(soup.find_all(class_="ProfileImage")[0]).split("\"")[3]
        try:
            rank = str(soup.find_all(class_="TierRank")[0]).split(">")[1].split("<")[0] + " " + str(soup.find_all(class_="LeaguePoints")[0]).split(">")[1].split("<")[0].replace("	", "").replace("\n", "") + " (" + str(soup.find_all(class_="WinRatio")[0]).split(">")[1].split("<")[0].replace("	", "").replace("\n", "") + ")"
        except Exception:
            rank = "Unranked"
        
        most_played = "**Most Played Champions:**"
        
        champs = soup.find_all(class_="ChampionBox Ranked")
        
        if(len(champs) > 5):
            champs = champs[:5]
        else:
            champs = champs[:len(champs)]
            
        for box in champs:
            #print(str(box) + "\n\n\n\n")
            champ_name = str(box).split("alt=\"")[1].split("\"")[0]
            games_played = str(box).split("class=\"Title\">")[1].split("</div>")[0].replace("	", "").replace("\n", "")
            winrate = str(box).split("title=\"Win Ratio\">")[1].split("</div>")[0].replace("	", "").replace("\n", "")
            
            most_played += f"\n{champ_name}: {winrate} *({games_played} Played)*"
            
        profile_embed = embed_creator.create_embed(rank, most_played, discord.Color.blue())
        profile_embed.set_author(name = "{}".format(" ".join(command)), url = url, icon_url = icon_url)
        #profile_embed.set_footer("Test")
        
        await message.channel.send(embed = profile_embed)
        
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
        await message.channel.send(embed = embed_creator.create_embed("Notice", "This command cannot be used in a server.", discord.Color.dark_red()))

# Load Commands
command_list = json.load(open(os.path.join(os.path.dirname(__file__), "./botcommands.json")))