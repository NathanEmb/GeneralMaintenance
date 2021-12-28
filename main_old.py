from sys import executable
import discord
from discord.player import FFmpegOpusAudio
import rolling_d20 as roll
from ctypes.util import find_library


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)   

    async def on_message(self, message):

        # don't respond to ourselves, tho that is kind of fun
        if message.author == self.user:
            return
       
       #admin block    
        if str(message.author) == 'Chasin#3684':
            if message.content == '!startup':
                await message.channel.send('Initializing.')
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
            if message.content == '!shutdown':
                await message.channel.send('Shutting down.')
                await self.close()

            if message.content == '!audio':
                await message.channel.send(str('Codec Loaded? '+str(discord.opus.is_loaded())))

        #Play ping pong!
        if message.content == 'ping':
            await message.channel.send('pong')

        #Read and send dice roll commands
        if message.content.startswith('!r'):
            await message.channel.send(roll.rolling_d20(message.content))
            
        if str(message.channel) == 'music-bot':
            if message.content == '!join':

                vchat = message.author.voice.channel
                vc = await vchat.connect()
                source = await discord.FFmpegOpusAudio.from_probe('BLACKPINK - How You Like That MV.webm',method='fallback', executable=r'C:\ffmpeg\bin\ffmpeg.exe')
                vc.play(source)
            else:
                pass



        if message.content == '!help':
            await message.channel.send("Hello! here are my current commands:\n\n 'ping' - I respond to you, cool\n'!r XdY' - I roll some dice for you \n '!echo' - I struggle to understand programming")


client = MyClient()

with open('myToken.txt', 'r') as pwd:
    token = pwd.read()

client.run(token)
