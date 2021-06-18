import discord
import rolling_d20

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
				
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')
	    
        if message.content.startswith('!r'):
            await message.channel.send(rolling_d20.rolling_d20())

client = MyClient()

with open('myToken.txt','r') as pwd:
    token = pwd.read()


client.run(token)
