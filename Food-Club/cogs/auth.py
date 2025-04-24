import discord
import os
import datetime
import json
from init_data import auth_users
from discord.ext import commands
from discord.ext.commands.context import Context

class Auth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def authorise(self, message, member : discord.Member):
        user = member.id

        if message.author.id in auth_users:
            with open("./local/auth.json", 'r') as f:
                auth = json.load(f)

            if not f'{user}' in auth:
                auth[f'{user}'] = {}
                auth[f'{user}']['name'] = str(member.name)
                auth[f'{user}']['auth'] = True

                with open("./local/auth.json", 'w') as f:
                    json.dump(auth, f, indent=4)
                embed = discord.Embed(description = f"{member.mention} was authorised.")
                await message.channel.send(embed = embed)

            elif f'{user}' in auth:
                auth[f'{user}']['auth'] = True

                with open("./local/auth.json", 'w') as f:
                    json.dump(auth, f, indent=4)
                embed = discord.Embed(description = f"{member.mention} was authorised.")
                await message.channel.send(embed = embed)

        else:
            await message.author.send(content = f'Oh! You are not authorised to use that')

    @commands.command()
    async def deauthorise(self, message, member : discord.Member):
        user = member.id

        if message.author.id in auth_users:
            with open("./local/auth.json", 'r') as f:
                auth = json.load(f)

            if f'{user}' in auth:
                auth[f'{user}']['auth'] = False

            with open("./local/auth.json", 'w') as f:
                json.dump(auth, f, indent=4)
            embed = discord.Embed(description = f"{member.mention} was deauthorised.")
            await message.channel.send(embed = embed)

        else:
            await message.author.send(content = f'Oh! You are not authorised to use that')

def setup(bot):
    bot.add_cog(Auth(bot))