import discord
import os
import datetime
import json
from init_data import role_id
from discord.ext import commands
from discord.ext.commands.context import Context

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.command()
async def verify(self, ctx, user : discord.Member):
    with open("./local/verified.json", "r") as f:
        users = json.load(f)

    if user in users:
        await ctx.send(f"`{user}` is already verified!")
    
    elif not user in users:
        id = user.id
        users.append(id)

        with open("./local/verified.json", "w") as f:
            json.dump(users, f, indent=4)

        guild = ctx.guild
        role = discord.utils.get(guild.roles, id=role_id)
        await user.add_roles(role)
        
        await ctx.send(f"`{user}` has been successfully verified")

def setup(bot):
    bot.add_cog(Verify(bot))