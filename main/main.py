import os
import sys
import discord
import commands
import json
import random

# Set Token And Prefix
token = sys.argv[1]
command_prefix = sys.argv[2]

# Get botinfo.json
bot_info = json.load(open(os.path.join(os.path.dirname(__file__), "./botinfo.json")))

class MyClient(discord.Client):
    
    async def on_ready(self):
        
        print(f"Logged on as {self.user}")
        # Change Status
        await self.change_presence(activity=discord.Game("v" + bot_info["version"]))

    async def on_message(self, message):
        
        # Set Default Priority To 0
        priority = 0
        
        # Don't Respond To Self
        if (message.author == self.user) or (message.author.bot):
            return
            
        else:
            
            # Get User's Priority
            for permission_level in bot_info["role_levels"]:
                
                # For Every Role Name In Each Permission Level
                for name in permission_level["names"]:
                    
                    # Get Role Name/ID Containing The Name
                    role = discord.utils.find(lambda r: r.name.lower() == name.lower(), message.guild.roles)
                    
                    # If The Role Is In The Author's Roles, They Have Said Permission Level
                    if(role in message.author.roles):
                        
                        priority = permission_level["level"]
            
            # Get Author Name And Discriminator
            name = f"{message.author.name}#{message.author.discriminator}"
            
            # Check Against Specific Administrators
            for n in bot_info["administrators"]:
                
                # If They're The Same, Set Permission Level Accordingly
                if(n["name"] == name):
                    priority = n["level"]
        
        # If Message Is A Command, Send It To Command Handler
        if(message.content[:1] == command_prefix):
            
            # [1:] Removes The Command Prefix
            await commands.handle_command(self, message, priority)
    
    async def on_voice_state_update(self, member, before, after):
        
        if after.channel != None and "New Channel" in after.channel.name:
            rand = random.randint(0000, 9999)
            category = discord.utils.get(member.guild.categories, name = "Voice Channels")
            await member.guild.create_voice_channel(f"Voice Channel ID: {rand}", category = category)
            channel = discord.utils.find(lambda r: r.name == f"Voice Channel ID: {rand}", member.guild.channels)
            await member.move_to(channel)
        
        elif before.channel != None and "Voice Channel ID: " in before.channel.name:
            if(len(before.channel.members) <= 0):
                await before.channel.delete()

# Start Client
client = MyClient()
client.run(token)