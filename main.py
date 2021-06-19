import discord
import rolling_d20 as roll
import connectionTest


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))

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

        #Testing discord commands outside of class?
        if message.content.startswith('!echo'):
            #connectionTest
            print("fu")

        if message.content == '!help':
            await message.channel.send("Hello! here are my current commands:\n\n 'ping' - I respond to you, cool\n'!r XdY' - I roll some dice for you \n '!echo' - I struggle to understand programming")


client = MyClient()

with open('myToken.txt', 'r') as pwd:
    token = pwd.read()

client.run(token)
