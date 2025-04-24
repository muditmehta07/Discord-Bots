import discord
import asyncio
from token import token
from init_data import watching_activity
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from itertools import cycle

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=watching_activity))

@bot.event
async def on_member_join(member):
    guild = bot.get_guild()
    channel = guild.get_channel()
    await channel.send(f'''Welcome {member.mention}! Glad to have you here!''',
                       file=discord.File('pic.png'))
    await member.send(f'''Welcome to {guild.name}, {member.name}!''')

@bot.event
async def on_member_remove(member):
    guild = bot.get_guild()
    channel = guild.get_channel()
    await channel.send(f'''Goodbye! {member.mention} has left the server.''')
    await member.send(f'''It was good to have you in {guild.name}! See ya!''')

bot.run(token)