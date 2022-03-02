import discord
from discord.ext import commands
from pytube import YouTube, Playlist
from pathlib import Path
import os
import asyncio
from datetime import datetime 
import platform

class MusicPlayer(commands.Cog):
    def __init__(self,bot):
        #Guild Specific data structures, each first level is guild ID
        self.bot = bot
        self.audio_clients = {}
        self.audio_queues = {}
        self.now_playing_msg = {}   
        self.music_channel = {}
        if platform.system() == 'Windows':   
            self.directory_symbol = '\\'
            self.codec_path = r"C:\ffmpeg\bin\ffmpeg.exe"
        elif platform.system() == 'Linux':
            self.directory_symbol = '/'
            self.codec_path = r"/bin/ffmpeg"
        else:
            print(platform.system())

    async def now_playing(self, ctx):
        #Get the music-bot channel object
        guild_channel = self.music_channel.get(ctx.guild.id)
        if not guild_channel:
            channels = ctx.guild.channels
            for chan in channels:
                if chan.name == 'music-bot':
                    self.music_channel[ctx.guild.id] = chan
                    break
        
        #Create queue message text string
        if len(self.audio_queues[ctx.guild.id]['files']) == 0:
            msg_text = "**There are no songs in queue.**"
        else:
            msg_text = '**There are ' + str(len(self.audio_queues[ctx.guild.id]['files'])-1) + ' songs in queue:**\n'
        
        for i,song in reversed(list(enumerate(self.audio_queues[ctx.guild.id]['files']))):
            if i == 0:
                msg_text = msg_text + '\n**Now Playing:\n **'
            start_spot = song.rfind(self.directory_symbol)
            song_name = song[(start_spot+1):]
            song_name = song_name[:-5]
            if i != 0:
                msg_text = msg_text + str(i) + '. ' + song_name + '\n'
            else:
                msg_text = msg_text + song_name + '\n'

        #Get existing message if it exists, update. If it doesn't exist, send one.
        guild_message = self.now_playing_msg.get(ctx.guild.id)
        if guild_message:
            print(msg_text)
            await guild_message.edit(content=msg_text)
        else:
            msg = await self.music_channel[ctx.guild.id].send(msg_text)
            self.now_playing_msg[ctx.guild.id] = msg
            await msg.add_reaction(emoji='⏯️')
            await msg.add_reaction(emoji='⏹️')            
            await msg.add_reaction(emoji='⏭️')

    def check_queue(self, ctx, client, audio_queue):
        #Remove the audio source that was just played
        audio_queue['sources'].pop(0)
        
        #If queue empty, clear it, and say so
        if audio_queue['sources'] == []:
            print('Queue depleted')
            try:
                os.remove(audio_queue['files'][0])
                print('Deleted File:',audio_queue['files'][0])
            except Exception as e: print(e)
            audio_queue['files'].pop(0)
            client.disconnect()
            coro1 = client.disconnect()
            fut1 = asyncio.run_coroutine_threadsafe(coro1, self.bot.loop)
            try:
                fut1.result
            except:
                print('Unable to process updating queue')

        #if not empty, play next song, clean up rest of files
        else:
            print('Playing next song')
            client.play(audio_queue['sources'][0],after=lambda x=0: self.check_queue(ctx,client,audio_queue))    
            #Delete audio file remove from file queue
            try:
                os.remove(audio_queue['files'][0])
                print('Deleted FIle:',audio_queue['files'][0])
            except Exception as e: print(e)
            audio_queue['files'].pop(0)
            print(audio_queue)

        #Running persistent queue message updater
        coro2 = self.now_playing(ctx)
        fut2 = asyncio.run_coroutine_threadsafe(coro2, self.bot.loop)
        try:
            fut2.result
        except:
            print('Unable to process updating queue')

    @commands.Cog.listener('on_reaction_add') 
    async def music_controls(self, reaction, user):
        if user == self.bot.user:
            return
        
        ctx = await self.bot.get_context(reaction.message)

        if reaction.message == self.now_playing_msg[reaction.message.guild.id]:
           #if play/pause 
            if reaction.emoji == '⏯️':
                if self.audio_clients[ctx.guild.id].is_playing():
                    self.audio_clients[ctx.guild.id].pause()
                elif self.audio_clients[ctx.guild.id].is_paused():
                    self.audio_clients[ctx.guild.id].resume()
                await reaction.remove(user)
            
            #if stop
            elif reaction.emoji == '⏹️':
                self.audio_clients[ctx.guild.id].pause()
                self.audio_queues[ctx.guild.id]['files'] = []
                self.audio_queues[ctx.guild.id]['sources'] = []
                await self.now_playing(ctx)
                await reaction.remove(user)

                for file in self.audio_queues[ctx.guild.id]['files']:
                    try:
                        os.remove(file)
                    except Exception as e: print(e)
            
            #if skip
            elif reaction.emoji == '⏭️':
                self.audio_clients[ctx.guild.id].pause()
                self.audio_queues[ctx.guild.id]['sources'].pop(0)
                try:
                    os.remove(self.audio_queues[ctx.guild.id]['files'][0])
                    print('Deleted FIle:',self.audio_queues[ctx.guild.id]['files'][0])
                except Exception as e: print(e)

                #remove audio, play next
                self.audio_queues[ctx.guild.id]['files'].pop(0)
                self.audio_clients[ctx.guild.id].play(self.audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: self.check_queue(ctx,self.audio_clients[ctx.guild.id],self.audio_queues[ctx.guild.id]))
                print(self.audio_queues[ctx.guild.id])
                await self.now_playing(ctx)
                await reaction.remove(user)

    @commands.Cog.listener('on_message') 
    async def queue_listener(self, message):
        ctx = await self.bot.get_context(message)
        if message.author == self.bot.user:
            return 
        
        if message.content.startswith('!') or message.content.startswith('?'):
            return

        #Takes a youtube link sent in music-bot channel and appends the audio source to guild specific queue

        if str(message.channel) == 'music-bot':
            current_location = Path(__file__).parent
            output_folder = current_location / 'music' / str(message.guild.id)
                        #Handles playlist links
            if 'youtube.com/playlist' in message.content or ('&playlist=' in message.content and 'youtube.com'):
                playlist = Playlist(message.content)
                await message.delete()

                for i,yt in enumerate(playlist.videos):
                    print(yt)
                    print(playlist)
                    print('Filtering audio streams', ' - ', datetime.now().strftime("%H:%M:%S"))
                    streams = yt.streams.filter(only_audio=True, audio_codec='opus')
                    print('Dowloading audio', ' - ', datetime.now().strftime("%H:%M:%S"))
                    audio_file = streams[0].download(output_path = (output_folder))
                    print('Audio dowloaded', ' - ', datetime.now().strftime("%H:%M:%S"))
                    self.audio_queues[ctx.guild.id]['files'].append(audio_file)
                    await self.now_playing(ctx)
                    print('Creating source', ' - ', datetime.now().strftime("%H:%M:%S"))
                    source = await discord.FFmpegOpusAudio.from_probe(audio_file,method='fallback', executable=self.codec_path)
                    self.audio_queues[ctx.guild.id]['sources'].append(source)
                    print('appending source', ' - ', datetime.now().strftime("%H:%M:%S"))
                    if not self.audio_clients[ctx.guild.id].is_playing() and not self.audio_clients[ctx.guild.id].is_paused():
                        self.audio_clients[ctx.guild.id].play(self.audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: self.check_queue(ctx,self.audio_clients[ctx.guild.id],self.audio_queues[ctx.guild.id]))
                    print(self.audio_queues[ctx.guild.id])
                    if i == 20:
                        break 

            elif 'youtube.com' in str(message.content) and ' ' not in str(message.content):
                if message.guild.id in self.audio_queues.keys() and message.guild.id in self.audio_clients.keys():
                    yt = YouTube(str(message.content))
                    await message.delete()
                    print('Filtering audio streams', ' - ', datetime.now().strftime("%H:%M:%S"))
                    streams = yt.streams.filter(only_audio=True, audio_codec='opus')
                    print('Dowloading audio', ' - ', datetime.now().strftime("%H:%M:%S"))
                    audio_file = streams[0].download(output_path = (output_folder))
                    print('Audio dowloaded', ' - ', datetime.now().strftime("%H:%M:%S"))
                    self.audio_queues[ctx.guild.id]['files'].append(audio_file)
                    await self.now_playing(ctx)
                    print('Creating source', ' - ', datetime.now().strftime("%H:%M:%S"))
                    source = await discord.FFmpegOpusAudio.from_probe(audio_file,method='fallback', executable=self.codec_path)
                    self.audio_queues[ctx.guild.id]['sources'].append(source)
                    print('appending source', ' - ', datetime.now().strftime("%H:%M:%S"))
                    #if not playing anything: play new link
                    if not self.audio_clients[ctx.guild.id].is_playing() and not self.audio_clients[ctx.guild.id].is_paused():
                        self.audio_clients[ctx.guild.id].play(self.audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: self.check_queue(ctx,self.audio_clients[ctx.guild.id],self.audio_queues[ctx.guild.id]))
                    print(self.audio_queues[ctx.guild.id])
            

            
            if self.directory_symbol not in message.content:
                await message.delete()

    @commands.command(aliases=['p','pl'],brief = 'Play YouTube link audio!')
    async def play(self, ctx, link):
        """Play a single youtube video/song link, OR play a playlist link eg: https://youtube.com/playlist?list="""
        #Look to see if any active voice clients, if not join where the user is
        if 'youtube' not in ctx.message.content:
            await ctx.send('I can only play full YouTube links with this command(ie: not shortened youtu.be links)')
            return
        
        #Get operating directory, (Guild specific)
        current_location = Path(__file__).parent
        output_folder = current_location / 'music' / str(ctx.guild.id)

        #Make Guild specific queue folder if doesn't already exist
        output_folder.mkdir(parents=True, exist_ok=True)

        #looks for voice client for guild the command came from
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        #if not already in voice, join voice that the user is in, sets up audio client
        if not voice_client:
            #if user isn't in voice channel
            if not ctx.author.voice:
                await ctx.send('Please join a voice channel!')
                return
            #join users voice channel
            else:
                voice_channel = ctx.author.voice.channel
                #add to audio client dictionary
                self.audio_clients[ctx.guild.id] = await voice_channel.connect()
        
        #sets up audio queue if necessary
        if ctx.guild.id not in self.audio_queues.keys():
            self.audio_queues[ctx.guild.id] = {'sources':[],'files':[]}

        if 'youtube.com/playlist' in ctx.message.content or ('&playlist=' in ctx.message.content and 'youtube.com'):
            playlist = Playlist(link)
            await ctx.message.delete()
            for i,yt in enumerate(playlist.videos):
                print(yt)
                print(playlist)
                print('Filtering audio streams', ' - ', datetime.now().strftime("%H:%M:%S"))
                streams = yt.streams.filter(only_audio=True, audio_codec='opus')
                print('Dowloading audio', ' - ', datetime.now().strftime("%H:%M:%S"))
                audio_file = streams[0].download(output_path = (output_folder))
                print('Audio dowloaded', ' - ', datetime.now().strftime("%H:%M:%S"))
                self.audio_queues[ctx.guild.id]['files'].append(audio_file)
                await self.now_playing(ctx)
                print('Creating source', ' - ', datetime.now().strftime("%H:%M:%S"))
                source = await discord.FFmpegOpusAudio.from_probe(audio_file,method='fallback', executable=self.codec_path)
                self.audio_queues[ctx.guild.id]['sources'].append(source)
                print('appending source', ' - ', datetime.now().strftime("%H:%M:%S"))
                if not self.audio_clients[ctx.guild.id].is_playing() and not self.audio_clients[ctx.guild.id].is_paused() :
                    self.audio_clients[ctx.guild.id].play(self.audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: self.check_queue(ctx,self.audio_clients[ctx.guild.id],self.audio_queues[ctx.guild.id]))
                print(self.audio_queues[ctx.guild.id])
                if i == 20:
                    break 
        
        #get YouTube Data    
        else:
            yt = YouTube(link)
            streams = yt.streams.filter(only_audio=True, audio_codec='opus')
            audio_file = streams[0].download(output_path = (output_folder))
            self.audio_queues[ctx.guild.id]['files'].append(audio_file)
            source = await discord.FFmpegOpusAudio.from_probe(audio_file,method='fallback', executable=self.codec_path)
            self.audio_queues[ctx.guild.id]['sources'].append(source)
            print(self.audio_queues[ctx.guild.id])
            await self.now_playing(ctx)

            #If we aren't already playing, start playing, otherwise just add to end of queue
            if not self.audio_clients[ctx.guild.id].is_playing() and not self.audio_clients[ctx.guild.id].is_paused():
                self.audio_clients[ctx.guild.id].play(self.audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: self.check_queue(ctx,self.audio_clients[ctx.guild.id],self.audio_queues[ctx.guild.id]))
            await ctx.message.delete()

    @commands.command()
    async def skip(self, ctx):
        """Skips the current song.  (Same as fast-forward button)"""
        self.audio_clients[ctx.guild.id].pause()
        self.audio_queues[ctx.guild.id]['sources'].pop(0)
        try:
            os.remove(self.audio_queues[ctx.guild.id]['files'][0])
            print('Deleted FIle:',self.audio_queues[ctx.guild.id]['files'][0])
        except Exception as e: print(e)

        #remove audio, play next
        self.audio_queues[ctx.guild.id]['files'].pop(0)
        self.audio_clients[ctx.guild.id].play(self.audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: self.check_queue(ctx,self.audio_clients[ctx.guild.id],self.audio_queues[ctx.guild.id]))
        print(self.audio_queues[ctx.guild.id])
        await self.now_playing(ctx)


    @commands.command()
    async def pause(self, ctx):
        """Pauses the current audio."""
        self.audio_clients[ctx.guild.id].pause()

    @commands.command()
    async def resume(self, ctx):
        """Resumes playing the current song/video."""
        self.audio_clients[ctx.guild.id].resume()

    @commands.command()
    async def clear(self, ctx):
        """Clears the queue of all items. (Same as stop button)"""
        self.audio_clients[ctx.guild.id].pause()
        for file in self.audio_queues[ctx.guild.id]['files']:
            try:
                os.remove(file)
            except Exception as e: print(e)

        self.audio_queues[ctx.guild.id]['files'] = []
        self.audio_queues[ctx.guild.id]['sources'] = []
        await self.now_playing(ctx)

    @commands.command(brief='Use this command to disconnect me from the voice channel. (coming soon...timeout)')
    async def leave(self, ctx):
        """Tells the bot to go away. Shoo!"""
        await ctx.voice_client.disconnect()

def setup(bot):
    bot.add_cog(MusicPlayer(bot))