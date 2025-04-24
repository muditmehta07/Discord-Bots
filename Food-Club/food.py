
import discord
import json
import datetime
from os import name
from token import token
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from itertools import cycle
from discord_components import DiscordComponents, Button, Select, SelectOption, ComponentsBot

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)
DiscordComponents(bot)
bot.remove_command('help')

initial_extensions = ['cogs.mod', 'cogs.auth', 'cogs.fun']

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Fruit Shop♡"))

# MEMBER JOIN


@bot.event
async def on_member_join(member):
    guild = bot.get_guild()
    channel = guild.get_channel()
    await channel.send(f'''{member.mention} Welcome to Fruit Shop♡! Hope you have a great time here!
    https://c.tenor.com/hHMA0O1_e_EAAAAM/anime-food.gif''')

# HELP COMMANDS


@bot.command()
async def help(message):

    embed = discord.Embed(
        description="**Welcome to Food Club! How may I help you?**\nChoose a section to go to...",
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_author(
        name="Food Club Help Index",
        icon_url=message.author.avatar_url
    )

    embed.set_thumbnail(url=bot.user.avatar_url)
    compmsg = await message.channel.send(embed=embed, components=[Select(
        placeholder="Club Index",
        options=[
                    SelectOption(label="🏠 General", value="1"),
                    SelectOption(label="🎮 Fun", value="2"),
                    SelectOption(label="🚨 Moderation", value="3")
        ],
        custom_id="StoreComponents"
    )])

    while True:
        interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == "StoreComponents", timeout=60)
        res = interaction.values[0]

        if res == "3" and interaction.user == message.author:
            modEmbed = discord.Embed(timestamp=datetime.datetime.utcnow())
            modEmbed.add_field(name="Kick 🦶🏻", value="-kick")
            modEmbed.add_field(name="Ban ❎", value="-ban")
            modEmbed.add_field(name="Unban ✅", value="-unban")
            modEmbed.add_field(name="Mute 🔇", value="-mute")
            modEmbed.add_field(name="Unmute 🔊", value="-unmute")
            modEmbed.add_field(name="Warn ❗", value="-warn")
            modEmbed.add_field(name="Warnings 📃", value="-warnings")
            modEmbed.add_field(name="Reset Warnings 🔁", value="-resetwarn")

            modEmbed.set_author(
                name="Moderation Commands 🚨",
                icon_url=message.author.avatar_url
            )

            await interaction.message.edit(embed=modEmbed, components=[Select(
                placeholder="Store Sections",
                options=[
                    SelectOption(label="🏠 General", value="1"),
                    SelectOption(label="🎮 Fun", value="2"),
                    SelectOption(label="🚨 Moderation", value="3")
                ],
                custom_id="StoreComponents"
            )])

            try:
                await interaction.respond()
            except:
                pass

        elif interaction.user != message.author:
            await interaction.send("This is not for you")

        else:
            await compmsg.edit(embed=embed, components=[Select(
                placeholder="Store Sections",
                options=[
                    SelectOption(label="🏠 General", value="1"),
                    SelectOption(label="🎮 Fun", value="2"),
                    SelectOption(label="🚨 Moderation", value="3")
                ],
                custom_id="StoreComponents", disabled=True
            )])
            await interaction.send("Interaction unavailable.")

bot.run(token)
