import discord
from token import token
from model import Assistant

chatbot = Assistant('./intents.json')
client = discord.Client()

if not os.path.exists('assistant_model.h5'):
    chatbot.train_model()
    chatbot.save_model('assistant_model')
else:
    chatbot.load_model('assistant_model')

@client.event
async def on_message(message, text):
    if not message.author == client.user:
        if text not in message.content:
            await message.channel.send(f"Usage : `faq {prompt}`")
        elif text in message.content:
            response = chatbot.process_input(text)
            await message.channel.send(response)

client.run(token)