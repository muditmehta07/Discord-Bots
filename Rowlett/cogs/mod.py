import discord
import datetime
import json
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.core import command
from discord.utils import get
from itertools import cycle

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        with open("./local/auth.json", 'r') as f:
            auth = json.load(f)

        userid = ctx.author.id
        try:
            if auth[str(userid)]['auth'] == True:
                await member.kick(reason=reason)

                embed = discord.Embed(title = "User Kicked 🦶🏻", description = f"*{ctx.author} kicked {member.display_name} from the server*")
                await ctx.send(embed = embed)

            else:
                await ctx.send(f"{ctx.author.mention} You are not authorised to do that!")
        except:
            await ctx.send(f"{ctx.author.mention} You are not authorised to do that!")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.User=None, reason =None):
        with open("./local/auth.json", 'r') as f:
            auth = json.load(f)

        userid = ctx.author.id
        try:
            if auth[str(userid)]['auth'] == True:
                if member == None or member == ctx.message.author:
                    embed = discord.Embed(title = "You cannot ban yourself ☹️")
                    await ctx.send(embed=embed)
                elif reason == None:
                    reason = "not following any rules"
                message = f"You have been banned from {ctx.guild.name} for {reason}"
                await member.send(message)
                await ctx.guild.ban(member, reason=reason)
                embed = discord.Embed(title = "User Banned 🚫", description = f"*{ctx.author} banned {member.display_name} from the server for {reason}*")
                await ctx.send(embed = embed)

            else:
                await ctx.send(f"{ctx.author.mention} You are not authorised to do that!")
        except:
            await ctx.send(f"{ctx.author.mention} You are not authorised to do that!")

    @commands.command()
    async def warn(self, message, member : discord.Member, reason : str = None):
        with open("./local/auth.json", 'r') as f:
            auth = json.load(f)

        userid = message.author.id

        content = message.message.content.replace(f"d.warn <@{member.id}>", "")

        if reason == None:
            reason = "Bad Behaviour"

        else:
            reason = content

        try:
            if auth[str(userid)]['auth'] == True:

                with open("./local/report.json", "r") as f:
                    users = json.load(f)

                try:
                    if str(member.id) not in users:
                        users[str(member.id)] = {}
                        users[str(member.id)]["name"] = member.name
                        users[str(member.id)]["count"] = 1
                        users[str(member.id)]["report1"] = reason
                        users[str(member.id)]["report2"] = None
                        users[str(member.id)]["report3"] = None

                        await message.channel.send(f'> `{member}` was warned!\n> Reason : **{reason}**')

                        with open("./local/report.json", 'w') as f:
                            json.dump(users, f, indent=4)

                    elif str(member.id) in users:
                        if users[str(member.id)]["count"] == 1:
                            users[str(member.id)]["count"] = 2
                            users[str(member.id)]["report2"] = reason
                            users[str(member.id)]["report3"] = None

                            await message.channel.send(f'> `{member}` was warned!\n> Reason : **{reason}**')

                            with open("./local/report.json", 'w') as f:
                                json.dump(users, f, indent=4)

                        elif users[str(member.id)]["count"] == 2:
                            users[str(member.id)]["count"] = 3
                            users[str(member.id)]["report3"] = reason

                            await message.channel.send(f'> `{member}` was warned!\n> Reason : **{reason}**\n```\n{member} has reached maximum number of warnings\n```')

                            with open("./local/report.json", 'w') as f:
                                json.dump(users, f, indent=4)

                        elif users[str(member.id)]["count"] == 3:
                            await message.channel.send(f'> `{member}` has already reached max warnings!')

                        else:
                            await message.channel.send(f"Something went wrong, try again later!")

                    else:
                        await message.channel.send(f"Something went wrong, try again later!")

                except Exception as e:
                    print(e)
                    await message.channel.send(f"{message.author.mention} Something went wrong, try again later!")

            else:
                await message.channel.send(f"{message.author.mention} You are not authorised to do that!")
        except Exception as e:
            print(e)
            await message.channel.send(f"{message.author.mention} You are not authorised to do that!")

    @commands.command(aliases = ["resetwarnings", "resetwarning"])
    async def resetwarn(self, ctx, member : discord.Member):
        with open("./local/auth.json", 'r') as f:
            auth = json.load(f)

        userid = ctx.author.id
        memid = member.id

        if not str(userid) in auth:
            await ctx.send(f"{ctx.author.mention} **You are not authorised to do that!**")

        if str(userid) in auth:
            if auth[str(userid)]['auth'] == True:

                with open("./local/report.json", "r") as f:
                    users = json.load(f)

                if not str(memid) in users:
                    await ctx.send(f"{ctx.author.mention} **LOL**\n```\nUser has 0 warnings!\n```")
                
                elif str(memid) in users:
                    del users[f'{memid}']
                    await ctx.send(f"{ctx.author.mention} Done! \n```\nUser's warnings have been reset!\n```")

                    with open("./local/report.json", "w") as f:
                        json.dump(users, f)
                
            else:
                await ctx.send(f"{ctx.author} You are not authorised to do that!")

    @commands.command(aliases = ["warning"])
    async def warnings(self, ctx, user : discord.Member):
        with open("./local/report.json", "r") as f:
            users = json.load(f)

        if str(user.id) in users:

            rep1 = users[f"{user.id}"]["report1"]
            rep2 = users[f"{user.id}"]["report2"]
            rep3 = users[f"{user.id}"]["report3"]

            string1 = ""
            if rep1 != None:
                string1 += f"**Reason** : `{rep1}`\n"
            
            if rep2 != None:
                string1 += f"**Reason** : `{rep2}`\n"

            if rep3 != None:
                string1 += f"**Reason** : `{rep3}`\n"

            await ctx.send(f"**{user.name}'s Warnings**\n{string1}")

        else:

            await ctx.send(f"**{user.name}** has 0 Warnings")

def setup(bot):
    bot.add_cog(Mod(bot))