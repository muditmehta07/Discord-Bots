from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay.display import Display
import asyncio
import datetime
import os
import json
from src.fetch import Fetch

class LoginError(Exception):
    def __init__(self):
        errorMessage = "LoginError: Invalid Credentials"
        return errorMessage
    
class dataScraper:
    def __init__(self, message, url, username, password, loginbutton, folder, bot, user):
        self.message = message
        self.url = url
        self.username = username
        self.password = password
        self.loginbutton = loginbutton
        self.folder = folder
        self.bot = bot
        self.user = user

    async def dataRefresh(self):
        timeout=3600
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(self.url)
        username_input = driver.find_element(By.NAME, "_UserName")
        password_input = driver.find_element(By.NAME, "_Password")
        login_button = driver.find_element(By.CLASS_NAME, self.loginbutton)

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        try:
            login_button.click()
        except Exception:
            errorMessage = LoginError()
            return errorMessage

        page_source = driver.page_source

        filename = os.path.join(self.folder, f"{self.user}.html")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(page_source)

        driver.quit()

        with open(f"./data/users.json", "r") as f:
            data = json.load(f)

        data[f"{self.user}"]["Last Update"] = str(datetime.datetime.utcnow())

        with open(f"./data/users.json", "w") as f:
            json.dump(data, f, indent=4)

        await self.message.channel.send("```swift\n> Logged in successfully!\n```")
        await Fetch.Organizer(self.bot, self.user)
        await asyncio.sleep(timeout)