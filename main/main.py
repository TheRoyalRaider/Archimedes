import os
import sys
import discord
import commands
import json

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
        if message.author == self.user:
            return
        else:
            # Get User's Priority
            name = f"{message.author.name}#{message.author.discriminator}"
            for n in bot_info["administrators"]:
                if(n["name"] == name):
                    priority = int(n["level"])
        
        # If Message Is A Command, Send It To Command Handler
        if(message.content[:1] == command_prefix):
            
            # [1:] Removes The Command Prefix
            await commands.handle_command(self, message, priority)
        
# Start Client
client = MyClient()
client.run(token)