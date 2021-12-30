import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='?')

cogs = ['MusicPlayer']

if __name__ == '__main__':
    for cog in cogs:
        bot.load_extension(cog)

@bot.event 
async def on_ready():
    print('Logged in as:',bot.user)

@bot.command(aliases = ['goodjob'], brief = 'Pat your bud on the back, anonymously!', help = 'type !gj @username and I will deliver some reassuring pats to the specified user.')
async def gj(ctx, user): 
    await ctx.message.delete()
    await ctx.send(f"Good Job {user}! *pat pat* \nhttps://media1.giphy.com/media/N0CIxcyPLputW/200.gif")
        
@bot.command(brief = 'Initialize Startup Sequence', hidden = True)
async def startup(ctx):
    await ctx.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))     

with open('myToken.txt', 'r') as pwd:
    token = pwd.read()

bot.run(token)

