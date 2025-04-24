from bs4 import BeautifulSoup
import json
import discord
import datetime
import re

class Fetch:
    async def timeElapsed(self, inputStr):
        inputDatetime = datetime.datetime.strptime(inputStr, "%Y-%m-%d %H:%M:%S.%f")
        inputDatetime = inputDatetime.replace(tzinfo=datetime.timezone.utc)
        currentDatetime = datetime.datetime.now(datetime.timezone.utc)
        timeDiff = currentDatetime - inputDatetime

        days = timeDiff.days
        seconds = timeDiff.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        result = ""
        if days > 0:
            result += f"{days} day{'s' if days > 1 else ''} "
        if hours > 0:
            result += f"{hours} hour{'s' if hours > 1 else ''} "
        if minutes > 0:
            result += f"{minutes} minute{'s' if minutes > 1 else ''} "
        if seconds > 0:
            result += f"{seconds} second{'s' if seconds > 1 else ''} "

        if result:
            result += "ago"
        else:
            result = "just now"

        return result


    async def elementFinder(self, _PATH, _CLASSNAME):
        try:
            li_elements = []

            with open(_PATH, "r", encoding="utf-8") as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, "html.parser")
            elements_with_class = soup.find_all(class_=_CLASSNAME)

            for element in elements_with_class:
                li_elements.extend(element.find_all("li"))

        except:
            li_elements = None

        return li_elements

    async def tableElementFinder(self, _PATH, _DIV):
        with open(_PATH, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")
        div_tag = soup.find("div", id=_DIV)

        if div_tag:
            table_elements = div_tag.find_all("table")
            return table_elements
        else:
            return []


    async def tableSearchTag(self, user, item):
        result = await self.tableElementFinder(f"./data/ami/{user}.html", item)
        if result == None:
            listofElements = None
        else:
            listofElements = []
            for li_element in result:
                listofElements.append(li_element.text)
        return listofElements

    async def dataOrganizer(self, user):
        result = await self.elementFinder(f"./data/ami/{user}.html", "item-list")
        if result == None:
            D = None
        else:
            listofElements = []
            for li_element in result:
                listofElements.append(li_element.text)

            data = listofElements

            newData = []
            newStartList = []
            for i in data:
                start = i[:10]
                for j in newData:
                    newStart = j[:10]
                    newStartList.append(newStart)
                if start not in newStartList:
                    newData.append(i)

            D = {}

            entryCounter = 1
            for entry in newData:
                courseCode = ""

                for c in entry:
                    if c == " ":
                        break
                    else:
                        courseCode += c

                entry = entry.replace(courseCode, "")
                courseCode = courseCode[2:]
                dataList = entry.split("\n\n")
                dataListNew = []

                for dataListEntry in dataList:
                    dataListEntry = dataListEntry.replace(" ", "")
                    dataListNew.append(dataListEntry)

                courseName = dataListNew[0]
                courseAttendanceTotalPattern = r"/(\d+)\)"
                courseAttendanceTotalMatch = re.search(
                    courseAttendanceTotalPattern, dataListNew[1]
                )

                courseAttendanceTotal = int(courseAttendanceTotalMatch.group(1))

                courseAttendancePresentPattern = r"\((\d+)/"
                courseAttendancePresentMatch = re.search(
                    courseAttendancePresentPattern, dataListNew[1]
                )

                courseAttendancePresent = int(courseAttendancePresentMatch.group(1))
                courseAttendanceAbsent = courseAttendanceTotal - courseAttendancePresent

                D[f"{entryCounter}"] = {}
                D[f"{entryCounter}"]["Course Code"] = courseCode
                D[f"{entryCounter}"]["Course Name"] = courseName
                D[f"{entryCounter}"][
                    "Attendance"
                ] = f"{round((courseAttendancePresent / courseAttendanceTotal) * 100, 2)}%"
                D[f"{entryCounter}"]["Total"] = courseAttendanceTotal
                D[f"{entryCounter}"]["Present"] = courseAttendancePresent
                D[f"{entryCounter}"]["Absent"] = courseAttendanceAbsent

                entryCounter += 1

        return D

    async def dayRemover(self, string):
        if "Monday" in string:
            string = string[6:]
        elif "Tuesday" in string:
            string = string[7:]
        elif "Wednesday" in string:
            string = string[8:]
        elif "Thursday" in string:
            string = string[8:]
        elif "Friday" in string:
            string = string[6:]
        else:
            string = None

        return string

    async def tableOrganizer(self, user):
        data = await self.tableSearchTag(user, "calendar")

        if data == None:
            D = None
        else:
            D = {}

            if data == None:
                print("No classes published")
            else:
                entry = data[0]
                entry = await self.dayRemover(entry)

                pattern = r"(\d{2}:\d{2} - \d{2}:\d{2})\s+(\w+)\s(.*?)\s((?:Mr|Dr|Prof|Ms|Mrs)..*?)\[(\d+)\]\s\(((?:LT|CR)-(?:\d{2}|\d{2}-\w)"
                entries = re.findall(pattern, entry)

                for entry in entries:
                    classTime = entry[0]
                    courseCode = entry[1]
                    courseName = entry[2]
                    facultyName = entry[3]
                    facultyCode = entry[4]
                    classRoom = entry[5]

                    D[f"{classTime}"] = {}
                    D[f"{classTime}"]["Course Code"] = courseCode
                    D[f"{classTime}"]["Course Name"] = courseName
                    D[f"{classTime}"]["Faculty Code"] = facultyCode
                    D[f"{classTime}"]["Faculty Name"] = facultyName
                    D[f"{classTime}"]["Location"] = classRoom

        return D


    async def Organizer(self, user):
        classData = await self.tableOrganizer(user)
        attData = await self.dataOrganizer(user)

        with open(f"./data/ttbl/{user}.json", "w") as f:
            json.dump(classData, f, indent=4, ensure_ascii=False)

        with open(f"./data/att/{user}.json", "w") as f:
            json.dump(attData, f, indent=4, ensure_ascii=False)


    async def onAttendanceUpdate(self, courseCode, status, att, user, bot):
        with open(f"./data/att/{user}.json", "r") as f:
            attData = json.load(f)

        with open(f"./data/users/{user}.json", "r") as f:
            userData = json.load(f)

        if status == "Present":
            color = 0x57F287
        elif status == "Absent":
            color = 0xED4245
        else:
            color = 0xF1C40F

        updateStatus = userData["Last Update"]
        time = await self.timeElapsed(updateStatus)

        courseName = attData[f"{courseCode}"]["Course Name"]
        faculty = attData[f"{courseCode}"]["Faculty"]

        embed = discord.Embed(
            description=f"**{faculty}** marked your `{status}`\n" f"Attendance: **{att}%**",
            color=color,
        )
        embed.set_footer(text=f"Updated {time}")
        embed.set_author(icon_url=bot.user.avatar.url, name=f"{courseName} Update")

        guildID = 735922425103122533
        channelID = 1135981891724529704
        guild = bot.get_guild(guildID)
        channel = guild.get_channel(channelID)
        await channel.send(embed=embed)