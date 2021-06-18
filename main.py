import discord
import rolling_d20 as roll


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):

        # don't respond to ourselves, tho that is kind of fun
        if message.author == self.user:
            return

        #Play ping pong!
        if message.content == 'ping':
            await message.channel.send('pong')

        #Read and send dice roll commands
        if message.content.startswith('!r'):
            await message.channel.send(roll.rolling_d20(message.content))



client = MyClient()

with open('myToken.txt', 'r') as pwd:
    token = pwd.read()

client.run(token)
