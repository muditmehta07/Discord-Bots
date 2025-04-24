import asyncio
import discord
import os
import datetime
import json
import random
import praw
from init_data import client_id, client_secret, user_agent
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, ComponentsBot, ButtonStyle
from discord.ext.commands.context import Context

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(self.bot)

    @commands.command()
    async def food(self, ctx):

        try:
            
            reddit = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent)
            memes_submissions = reddit.subreddit("foodporn").hot()
            post = random.randint(1, 100)
            for i in range(0, post):
                submission = next(x for x in memes_submissions if not x.stickied)

            if submission.url.endswith('.png') or submission.url.endswith('.jpg') or submission.url.endswith('.gif'):
                embed = discord.Embed(title = "Yum 🤤",
                timestamp=datetime.datetime.utcnow())

                embed.set_footer(text=ctx.author)
                embed.set_image(url=f"{submission.url}")

                await ctx.send(embed=embed, components=[Button(style=ButtonStyle.blue, label="Next", custom_id= "StoreComponents"), Button(style=ButtonStyle.gray, label="End", custom_id= "StoreComponents2")])

                while True:   
                    memes_submissions2 = reddit.subreddit("foodporn").hot()
                    post2 = random.randint(1, 100)
                    for i in range(0, post2):
                        submission2 = next(x for x in memes_submissions2 if not x.stickied)
                    
                    embed2 = discord.Embed(title = "Yumm 🤤",
                    timestamp=datetime.datetime.utcnow())

                    embed2.set_footer(text=ctx.author)
                    embed2.set_image(url=f"{submission2.url}")   

                    inter = await self.bot.wait_for('button_click', timeout=120)
                    if inter.custom_id == "StoreComponents" and inter.user == ctx.author:
                        await inter.message.edit(embed = embed2, components=[Button(style=ButtonStyle.blue, label="Next", custom_id= "StoreComponents", disabled=False), Button(style=ButtonStyle.gray, label="End", custom_id= "StoreComponents2", disabled=False)])
                        try:
                            await inter.respond()
                        except:
                            pass

                    elif inter.custom_id == "StoreComponents2" and inter.user == ctx.author:
                        await inter.message.edit(components=[Button(style=ButtonStyle.blue, label="Next", custom_id= "StoreComponents", disabled=True), Button(style=ButtonStyle.gray, label="End", custom_id= "StoreComponents2", disabled=True)])
                        try:
                            await inter.respond()
                        except:
                            pass
                        break
                    else:
                        await inter.send("This is not for you")
            else:
                await ctx.send(f'Called by : {ctx.author}\nTitle : {submission.title}\n{submission.url}')
        except Exception as e:
            await ctx.author.send(f"{e}")

def setup(bot):
    bot.add_cog(Fun(bot))