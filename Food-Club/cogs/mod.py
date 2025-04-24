import discord
from discord.ext import commands
import os
import datetime
import json

from discord.ext.commands.context import Context

class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)

        embed = discord.Embed(title = "User Kicked 🦶🏻", description = f"*{ctx.author} kicked {member.display_name} from the club*")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(ctx, member:discord.User=None, reason =None):
        if member == None or member == ctx.message.author:
            embed = discord.Embed(title = "You cannot ban yourself ☹️")
            await ctx.send(embed=embed)
        elif reason == None:
            reason = "not following any rules"
        message = f"You have been banned from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(title = "User Banned 🚫", description = f"*{ctx.author} banned {member.display_name} from the club for {reason}*")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(ctx, *, member : discord.Member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
        
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed = discord.Embed(title = "User Unbanned 😄", description = f"*{ctx.author} unbanned {member.display_name} from the club*")
                await ctx.channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mute(ctx, member: discord.Member, *, reason=None):
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted User")

        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted User")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
        embed = discord.Embed(title="User Muted 🔇", description=f"*{member.display_name} has been muted*")
        embed.add_field(name="reason:", value=reason, inline=False)
        await ctx.send(embed=embed)
        await member.add_roles(mutedRole, reason=reason)
        await member.send(f" You have been muted from: `Food Club` reason: {reason}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unmute(ctx, member: discord.Member):
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted User")

        await member.remove_roles(mutedRole)
        await member.send(f" you have unmutedd from: - {ctx.guild.name}")
        embed = discord.Embed(title="User Unmuted 🔊", description=f"*{member.display_name} has been unmuted*")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def warn(self, message, member : discord.Member, reason : str = "Bad Behaviour"):
        with open("./local/auth.json", 'r') as f:
            auth = json.load(f)

        userid = message.author.id
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

                        await message.channel.send(f'{member} was warned!\nReason : `{reason}`')

                        with open("./local/report.json", 'w') as f:
                            json.dump(users, f, indent=4)

                    elif str(member.id) in users:
                        if users[str(member.id)]["count"] == 1:
                            users[str(member.id)]["count"] = 2
                            users[str(member.id)]["report2"] = reason
                            users[str(member.id)]["report3"] = None

                            await message.channel.send(f'{member} was warned!\nReason : `{reason}`')

                            with open("./local/report.json", 'w') as f:
                                json.dump(users, f, indent=4)

                        elif users[str(member.id)]["count"] == 2:
                            users[str(member.id)]["count"] = 3
                            users[str(member.id)]["report3"] = reason

                            await message.channel.send(f'{member} has reached the maximum warnings')

                            with open("./local/report.json", 'w') as f:
                                json.dump(users, f, indent=4)

                        elif users[str(member.id)]["count"] == 3:
                            await message.channel.send(f'{member} has already reached max warnings!')

                        else:
                            await message.channel.send(f"{member} Something went wrong, try again later!")

                    else:
                        await message.channel.send(f"{member} Something went wrong, try again later!")

                except Exception as e:
                    print(e)
                    await message.channel.send(f"{message.author} Something went wrong, try again later!")

            else:
                await message.channel.send(f"{message.author} You are not authorised to do that!")
        except Exception as e:
            print(e)
            await message.channel.send(f"{message.author} You are not authorised to do that!")


    @commands.command(aliases = ["resetwarnings", "resetwarning"])
    async def resetwarn(self, ctx, member : discord.Member):
        with open("./local/auth.json", 'r') as f:
            auth = json.load(f)

        userid = ctx.author.id
        memid = member.id

        if not str(userid) in auth:
            await ctx.send(f"{ctx.author} You are not authorised to do that!")

        if str(userid) in auth:
            if auth[str(userid)]['auth'] == True:

                with open("./local/report.json", "r") as f:
                    users = json.load(f)

                if not str(memid) in users:
                    await ctx.send(f"{ctx.author} User has 0 warnings!")
                
                elif str(memid) in users:
                    del users[f'{memid}']
                    await ctx.send(f"{ctx.author} User's warnings have been reset!")

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
    bot.add_cog(ModCog(bot))