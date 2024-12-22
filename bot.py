import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'announce_channel': None}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.tree.command(name="setup", description="Setup the announcement channel")
async def setup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return

    class ChannelSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        async def on_timeout(self):
            try:
                await interaction.edit_original_response(content="Setup timed out!", view=None)
            except:
                pass

    class ChannelSelectCallback(discord.ui.ChannelSelect):
        def __init__(self):
            super().__init__(
                placeholder="Select announcement channel",
                channel_types=[discord.ChannelType.text]
            )

        async def callback(self, interaction: discord.Interaction):
            channel = self.values[0]
            config = load_config()
            config['announce_channel'] = channel.id
            save_config(config)
            
            await interaction.response.send_message(f"Setup complete! I'll now announce new joins in {channel.mention}")
            self.view.stop()

    view = ChannelSelectView()
    view.add_item(ChannelSelectCallback())
    
    await interaction.response.send_message("Please select the channel for sale announcements:", view=view)

@bot.event
async def on_member_join(member):
    config = load_config()
    if config['announce_channel']:
        announce_channel = bot.get_channel(config['announce_channel'])
        if announce_channel:
            await announce_channel.send("축하합니다! 세일을 만드셨습니다! 💰 ⚡")

bot.run(os.getenv('DISCORD_TOKEN')) 