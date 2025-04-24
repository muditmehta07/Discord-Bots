import discord
import json
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.core import command
from discord.utils import get
from init_data import auth_guild, invite_link

class Gen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, message):
            embed = discord.Embed(title = "Invite",
            description = "Click the link above to invite me!", 
            url = invite_link)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_author(name = message.author, icon_url = message.author.avatar_url)
            await message.channel.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        if ctx.guild.id in auth_guild:
            with open("./local/welcome.json", "r") as f:
                file = json.load(f)

            channel = ctx.channel.id
            message = "Welcome, Dear Devotee, to our wonderful and ever expanding Discord Server.\n\nWe have built up a digital library named Tattvavada E-library.\n\nHere, we've compiled various scriptures and works of Madhwa Yatis including Sarvamoola Granthas, Sriman Nyaya Sudha, Pratah Sankalpa Gadya, Raghavendra Vijaya and many more along with English translations. You'll be able to access all these books for free. We are even publishing Sarvamoola Granthas in 9 Indian languages.\n\nHere's the link to the website\nhttps://tattvavadalibrary.wordpress.com/\nInviting you all to make use of these resources. Feedback and suggestions are welcome.\n\nYou can also let us know in case you need any particular book and we'll try to make it available on the website.\n\nHari Sarvothama! Vayu Jeevothama!"

            file["channel"] = channel
            file["message"] = message

            with open("./local/welcome.json", "w") as f:
                json.dump(file, f)

            await ctx.send("This channel has been set as your welcome channel")
        
        else:
            await ctx.send("Command only available for 1 server")

def setup(bot):
    bot.add_cog(Gen(bot))