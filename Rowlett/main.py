import discord
import json
import datetime
from token import token
from discord.enums import ActivityType
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from itertools import cycle
from discord import message
from discord.ext.commands.context import Context

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('d.'), intents = intents)
bot.remove_command('help')

initial_extensions = ['cogs.mod', 'cogs.auth', 'cogs.gen', 'cogs.verify']

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_member_join(member):
    try:
        id = member.guild.id
        with open("./local/welcome.json", 'r') as f:
            welcome = json.load(f)

        with open("./local/auth.json", 'r') as g:
            auth = json.load(g)
            
        channelid = welcome['channel']
        msg = welcome['message']
        guild = bot.get_guild(id)
        channel = guild.get_channel(channelid)
        embed = discord.Embed(description = f'Hey {member.mention}! {msg}', 
        timestamp=datetime.datetime.utcnow())
        embed.set_author(name = member, icon_url= member.avatar_url)
        await channel.send(embed=embed)
    except:
        pass

@bot.command()
async def help(message):
    embed = discord.Embed(description = "**General**: d.gen\n**Moderation**: d.mod", timestamp = datetime.datetime.utcnow())
    embed.set_author(name = "Help Commands", icon_url = bot.user.avatar_url)
    await message.channel.send(embed = embed)

@bot.command(aliases = ["g", "gen"])
async def general(message):
    replyEmoji = bot.get_emoji(929383454469128263)
    embed = discord.Embed(timestamp = datetime.datetime.utcnow(),
    description = f"**d.welcome**\n{replyEmoji}Set as welcome channel\n**d.invite**\n{replyEmoji}Get invite link\n**d.ping**\n{replyEmoji}Get bot's ping")
    embed.set_author(name = "General", icon_url = bot.user.avatar_url)
    await message.channel.send(embed = embed)

@bot.command(aliases = ["m", "mod"])
async def moderation(message):
    replyEmoji = bot.get_emoji(929383454469128263)
    embed = discord.Embed(timestamp = datetime.datetime.utcnow(),
    description = f"**d.kick**\n{replyEmoji}Kick a user\n**d.ban**\n{replyEmoji}Ban a user\n**d.warn**\n{replyEmoji}Warn a user\n**d.warnings**\n{replyEmoji}View a user's warnings\n**d.resetwarn**\n{replyEmoji}Reset a user's warnings")
    embed.set_author(name = "Moderation", icon_url = bot.user.avatar_url)
    await message.channel.send(embed = embed)

@bot.command()
async def authusers(ctx : Context):
    if ctx.author.id == 488996680058798081 or ctx.author.id == 601590347180539925:
        with open("./local/auth.json", "r") as f:
            users = json.load(f)

        L = ""
        count = 1
        for i in users:
            if users[str(i)]["auth"] == True:
                i = int(i)
                name = bot.get_user(i)
                L += f"**{count}.** `{name}`\n"
                count+=1

        await ctx.send(f"**Auth List**\n{L}")

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency*1000)} ms')

bot.run(token)