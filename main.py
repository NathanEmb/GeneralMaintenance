import discord
from discord.ext import commands
from pytube import YouTube
from pathlib import Path
import os


bot = commands.Bot(command_prefix='!')

#Music bot data structures
#Contains VoiceClients for each server (how you access play/pause/resume/etc)
audio_clients = {}

#Contains AudioSource and their connected  audio file path
audio_queues = {}


def check_queue(ctx,client,audio_queue):
    #Remove the audio source that was just played
    audio_queue['sources'].pop(0)
    
    if audio_queue['sources'] == []:
        print('Queue depleted')
        try:
            os.remove(audio_queue['files'][0])
            print('Deleted FIle:',audio_queue['files'][0])
        except Exception as e: print(e)
        audio_queue['files'].pop(0)

    else:
        print('Playing next song')
        client.play(audio_queue['sources'][0],after=lambda x=0: check_queue(ctx,client,audio_queue))    
        #Delete audio file remove from file queue
        try:
            os.remove(audio_queue['files'][0])
            print('Deleted FIle:',audio_queue['files'][0])
        except Exception as e: print(e)
        audio_queue['files'].pop(0)
        print(audio_queue)



@bot.event 
async def on_ready():
    print('Logged in as:',bot.user)

@bot.listen('on_message') 
async def queue_listener(message):
    if message.author == bot.user:
        return 

    #Takes a youtube link sent in music-bot channel and appends the audio source to guild specific queue
    current_location = Path(__file__).parent
    output_folder = current_location / 'music' / str(message.guild.id)
    if 'https://www.youtube.com/watch' in str(message.content) and ' ' not in str(message.content):
        if str(message.channel) == 'music-bot':
            if message.guild.id in audio_queues.keys() and message.guild.id in audio_clients.keys():
                yt = YouTube(str(message.content))
                streams = yt.streams.filter(only_audio=True, audio_codec='opus')
                audio_file = streams[0].download(output_path = (output_folder))
                source = await discord.FFmpegOpusAudio.from_probe(audio_file,method='fallback', executable='/bin/ffmpeg')
                audio_queues[message.guild.id]['files'].append(audio_file)
                audio_queues[message.guild.id]['sources'].append(source)

                #if not playing anything: play new link
                if not audio_clients[message.guild.id].is_playing():
                    audio_clients[message.guild.id].play(audio_queues[message.guild.id]['sources'][0],after=lambda x=0: check_queue(message,audio_clients[message.guild.id],audio_queues[message.guild.id]))
                print(audio_queues[message.guild.id])

@bot.command(aliases=['p','pl'],brief = 'Play YouTube link audio!')
async def play(ctx, link):
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
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    #if not already in voice, join voice that the user is in, sets up audio clinet
    if not voice_client:
        #if user isn't in voice channel
        if not ctx.author.voice:
            await ctx.send('Please join a voice channel!')
            return
        #join users voice channel
        else:
            voice_channel = ctx.author.voice.channel
            #add to audio client dictionary
            audio_clients[ctx.guild.id] = await voice_channel.connect()
    
    #sets up audio queue if necessary
    if ctx.guild.id not in audio_queues.keys():
        audio_queues[ctx.guild.id] = {'sources':[],'files':[]}

    
    #get YouTube Data    
    yt = YouTube(link)
    streams = yt.streams.filter(only_audio=True, audio_codec='opus')
    audio_file = streams[0].download(output_path = (output_folder))
    audio_queues[ctx.guild.id]['files'].append(audio_file)
    source = await discord.FFmpegOpusAudio.from_probe(audio_file,method='fallback', executable='/bin/ffmpeg')
    audio_queues[ctx.guild.id]['sources'].append(source)
    print(audio_queues[ctx.guild.id])

    #If we aren't already playing, start playing, otherwise just add to end of queue
    if not audio_clients[ctx.guild.id].is_playing():
        audio_clients[ctx.guild.id].play(audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: check_queue(ctx,audio_clients[ctx.guild.id],audio_queues[ctx.guild.id]))

@bot.command()
async def skip(ctx):
    audio_clients[ctx.guild.id].pause()
    audio_queues[ctx.guild.id]['sources'].pop(0)
    try:
        os.remove(audio_queues[ctx.guild.id]['files'][0])
        print('Deleted FIle:',audio_queues[ctx.guild.id]['files'][0])
    except Exception as e: print(e)

    #remove audio, play next
    audio_queues[ctx.guild.id]['files'].pop(0)
    audio_clients[ctx.guild.id].play(audio_queues[ctx.guild.id]['sources'][0],after=lambda x=0: check_queue(ctx,audio_clients[ctx.guild.id],audio_queues[ctx.guild.id]))
    print(audio_queues[ctx.guild.id])

@bot.command(aliases = ['q'])
async def queue(ctx):
    temp = audio_queues[ctx.guild.id]['files']
    msg_text = 'There are ' + str(len(temp)) + ' songs in queue:\n'
    
    for i,song in enumerate(temp):
        start_spot = song.rfind('/')
        song_name = song[(start_spot+1):]
        song_name = song_name[:-5]
        msg_text = msg_text + str(i+1) + '. ' + song_name + '\n'
    
    await ctx.send(msg_text)



@bot.command()
async def pause(ctx):
    audio_clients[ctx.guild.id].pause()

@bot.command()
async def resume(ctx):
    audio_clients[ctx.guild.id].resume()

@bot.command()
async def clear(ctx):
    audio_clients[ctx.guild.id].pause()
    for file in audio_queues[ctx.guild.id]['files']:
        try:
            os.remove(file)
        except Exception as e: print(e)

    audio_queues[ctx.guild.id]['files'] = []
    audio_queues[ctx.guild.id]['sources'] = []

@bot.command(brief='Use this command to disconnect me from the voice channel. (coming soon...timeout)')
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command(aliases = ['goodjob'], brief = 'Pat your bud on the back, anonymously!', help = 'type !gj @username and I will deliver some reassuring pats to the specified user.')
async def gj(ctx, user):
    
    await ctx.message.delete()
    await ctx.send(f"Good Job {user}! *pat pat*")
        
@bot.command(brief = 'Initialize Startup Sequence', hidden = True)
async def startup(ctx):
    await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))   

    current_location = Path(__file__).parent
    output_folder = current_location / 'music'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)      

with open('myToken.txt', 'r') as pwd:
    token = pwd.read()

bot.run(token)
queue = {}
