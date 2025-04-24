import discord
import json
import asyncio
import os
from discord.ext import commands
from src.login import *
from src.fetch import Fetch

intents = discord.Intents().all()
client = discord.Client(intents=intents)
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)
bot.remove_command("help")

class Amizone:
    def __init__(self, url, button, folder):
        self.url = url
        self.button = button
        self.folder = folder
        self.TASKS = []

    async def responseMessage(self, subjectCode, user):
        with open(f"./data/users.json", "r") as f:
            userData = json.load(f)

        updateStatus = userData[f"{user}"]["Last Update"]
        time = await Fetch().timeElapsed(updateStatus)

        with open(f"./data/att/{user}.json", "r") as f:
            attData = json.load(f)

        att = attData[subjectCode]["Attendance"]
        pre = attData[subjectCode]["Present"]
        abe = attData[subjectCode]["Absent"]
        tot = attData[subjectCode]["Total"]
        courseName = attData[subjectCode]["Course Name"]

        present = int(pre)
        total = int(tot)
        percent = (present / total) * 100

        toAttend = 0
        if percent >= 75.00:
            toAttend = 0
        else:
            while 75.00 > percent:
                present += 1
                total += 1
                toAttend += 1
                percent = (present / total) * 100

        presentFail = int(pre)
        totalFail = int(tot) + 1
        percentFail = (presentFail / totalFail) * 100

        toAttendFail = 0
        if percentFail >= 75.00:
            toAttendFail = 0
        else:
            while 75.00 > percentFail:
                presentFail += 1
                totalFail += 1
                toAttendFail += 1
                percentFail = (presentFail / totalFail) * 100

        embed = discord.Embed(
            description=f"> **Attend `{toAttend}` classes for 75%+ attendance**\n> **Fail to attend `1` class, you'll have to attend `{toAttendFail}` more for 75%+ attendance**\n",
            color=0xF1C40F,
        )

        embed.add_field(
            name="__Attendance__",
            value=f"**Percent** : `{round(((pre/tot)*100), 2)}%`\n"
            f"**Present** : `{pre}/{tot}`\n"
            f"**Absent** : `{abe}/{tot}`",
            inline=False,
        )

        embed.set_footer(text=f"Updated {time}")
        embed.set_author(icon_url=bot.user.avatar.url, name=f"{courseName}")

        return embed

AMIZONE = Amizone(
    url="https://s.amizone.net/",
    button="login100-form-btn",
    folder="./data/ami/"
)

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="amizone.net"
        )
    )

    with open("./data/users.json", "r") as f:
        data = json.load(f)

    for users in data:
        data[users]["Tasks"] = None

    with open("./data/users.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_message(message):
    if message.author.bot == False:
        await bot.process_commands(message)

@bot.command(aliases=["h"])
async def help(message):
    user = message.author.id

    with open("./data/users.json", "r") as f:
        users = json.load(f)

    if str(user) in users:
        lastUpdate = users[f"{user}"]["Last Update"]
        elapsed = await Fetch().timeElapsed(lastUpdate)

        taskBool = users[f"{user}"]["Tasks"]
        if taskBool == None:
            embed = discord.Embed(
                description="> Your data is not updated. Use `?login` to refresh",
                color=0xF1C40F,
            )
        else:
            embed = discord.Embed(color=0xF1C40F)
        embed.add_field(name="Attendance", value="`?sub`")
        embed.add_field(name="Time Table", value="`?tt`")
        embed.set_author(icon_url=bot.user.avatar.url, name="Help Commands")
        embed.set_footer(text=f"Updated {elapsed}")
        await message.channel.send(embed=embed)
    else:
        embed = discord.Embed(
            description="> We require your Amizone credentials in order to fetch your data (*duh?*)",
            color=0xF1C40F,
        )
        embed.add_field(
            name="Login Command", value="`?login <username> <password>`", inline=False
        )
        embed.set_author(icon_url=bot.user.avatar.url, name="Login Help")
        await message.channel.send(embed=embed)


@bot.command()
async def login(message, username=None, password=None):
    if message.author.bot == False:
        user = message.author.id
        user = str(user)
        userPath = f"./data/users.json"
        userTablePath = f"./data/ttbl/{user}.json"
        userAttendancePath = f"./data/att/{user}.json"

        with open(userPath, "r") as f:
            userDict = json.load(f)

        if (username == None) and (password == None) and (user not in userDict):
            await message.channel.send(
                "```swift\n> Login Error!\nYou must enter your credentials\nUse command ?help to learn more\n```"
            )

        elif user not in userDict:
            userDict[user] = {}
            userDict[user]["Username"] = username
            userDict[user]["Password"] = password
            userDict[user]["Discord ID"] = message.author.name
            userDict[user]["Tasks"] = None
            userDict[user]["Last Update"] = None
            userDict[user]["Enabled"] = True

            with open(f"{userPath}", "w") as f:
                json.dump(userDict, f, indent=4)

        elif user in userDict:
            username, password = userDict[user]["Username"], userDict[user]["Password"]

        if not os.path.exists(userTablePath):
            userDict = {}

            with open(f"{userTablePath}", "w") as f:
                json.dump(userDict, f, indent=4)

        if not os.path.exists(userAttendancePath):
            userDict = {}

            with open(f"{userAttendancePath}", "w") as f:
                json.dump(userDict, f, indent=4)

        await message.channel.send("```swift\n> Your request is being processed\n```")
        with open(f"{userPath}", "r") as f:
            data = json.load(f)

        if data[user]["Tasks"] == None:
            try:
                task = dataScraper(
                        message,
                        AMIZONE.url,
                        username,
                        password,
                        AMIZONE.button,
                        AMIZONE.folder,
                        bot,
                        int(user),
                    )
                thread = asyncio.create_task(task.dataRefresh())
                AMIZONE.TASKS.append(thread)

                data[user]["Tasks"] = True
                with open(f"{userPath}", "w") as f:
                    json.dump(data, f, indent=4)
        
            except Exception as e:
                data[user]["Tasks"] = None
                with open(f"{userPath}", "w") as f:
                    json.dump(data, f, indent=4)
                await message.channel.send(f"{e}")

        elif data[user]["Tasks"] == True:
            await message.channel.send("```swift\nAlready logged in.\n```")

@bot.command(aliases=["time", "table", "tt"])
async def timetable(message):
    user = message.author.id
    with open(f"./data/ttbl/{user}.json", "r") as f:
        data = json.load(f)

    with open(f"./data/users.json", "r") as f:
        userData = json.load(f)

    updateStatus = userData[f"{user}"]["Last Update"]
    elapsed = await Fetch().timeElapsed(updateStatus)

    dataString = ""

    timeList = [i for i in data]

    for time in timeList:
        courseCode = data[f"{time}"]["Course Code"]
        courseName = data[f"{time}"]["Course Name"]
        facultyCode = data[f"{time}"]["Faculty Code"]
        facultyName = data[f"{time}"]["Faculty Name"]
        classRoom = data[f"{time}"]["Location"]

        dataString += f"__**{time}**__\n**Course:** {courseName} `{courseCode}`\n**Faculty:** {facultyName} `{facultyCode}`\n**Location:** {classRoom}\n\n"

    taskBool = userData[f"{user}"]["Tasks"]
    if taskBool == None:
        embed = discord.Embed(
            description=f"> Your data is not updated. Use `?login` to refresh\n\n{dataString}",
            color=0xF1C40F,
        )
    else:
        embed = discord.Embed(description=f"{dataString}", color=0xF1C40F)

    embed.set_footer(text=f"Updated {elapsed}")
    embed.set_author(
        icon_url=bot.user.avatar.url,
        name=f"{message.author.global_name}'s Time Table",
    )
    await message.channel.send(embed=embed)

@bot.group(invoke_without_command=True)
async def sub(message, option=None):
    user = message.author.id
    with open(f"./data/att/{user}.json", "r") as f:
        data = json.load(f)

    with open(f"./data/users.json", "r") as f:
        userData = json.load(f)

    updateStatus = userData[f"{user}"]["Last Update"]
    time = await Fetch().timeElapsed(updateStatus)

    keyList = [i for i in data]

    if option == None:
        dataString = ""
        counter = 1

        for i in keyList:
            courseName = data[f"{i}"]["Course Name"]
            courseCode = data[f"{i}"]["Course Code"]
            myAttendance = data[f"{i}"]["Attendance"]
            myTotal = data[f"{i}"]["Total"]
            myPresent = data[f"{i}"]["Present"]
            myAbsent = data[f"{i}"]["Absent"]

            dataString += f"**{counter}. {courseName}**-> `({myPresent}/{myTotal}) {myAttendance}`\n"
            counter += 1

        taskBool = userData[f"{user}"]["Tasks"]
        if taskBool == None:
            embed = discord.Embed(
                description=f"> Your data is not updated. Use `?login` to refresh\n\n{dataString}\nUse command `?sub <number>` to get info on a particular subject",
                color=0xF1C40F,
            )
        else:
            embed = discord.Embed(
                description=f"{dataString}Use command `?sub <number>` to get info on a particular subject",
                color=0xF1C40F,
            )

        embed.set_footer(text=f"Updated {time}")
        embed.set_author(
            icon_url=bot.user.avatar.url, name=f"{message.author.global_name}'s Courses"
        )
        await message.channel.send(embed=embed)

    elif str(option) in keyList:
        courseCode = str(option)
        embed = await AMIZONE.responseMessage(str(courseCode), user=user)
        await message.channel.send(embed=embed)

@bot.command(aliases=["senduser"])
async def sendusers(message):
    if message.author.id == 488996680058798081:
        file = discord.File("./data/users.json")
        await message.channel.send(file=file)

@bot.command()
async def updateusers(message):
    if message.author.id == 488996680058798081:
        try:
            await message.message.attachments[0].save(fp="./update.json")
            with open("./update.json", "r") as f:
                data = json.load(f)

            with open("./data/users.json", "w") as f2:
                json.dump(data, f2, indent=4)

            await message.channel.send(content="Users Updated")
        except Exception as e:
            await message.channel.send(f"Failed. Error : {str(e)}")

        os.remove("./update.json")

bot.run("")