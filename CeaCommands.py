from discord.ext import commands
from RequestManager import get_org_teams
import operator

class CeaCommands(commands.Cog):
    def __init__(self,bot):

        self.bot = bot
        self.headers = {'User-Agent':'GM_Stats'}
        self.endpoint = {'url':'https://1ebv8yx4pa.execute-api.us-east-1.amazonaws.com/prod/','Header':self.headers}
        self.brackets = {
            'Rocket League':{'s2022-legacy':'vsrMjnFDMc','s2022-contenders':'WZaqjbfPLL'},
            'Valorant': {'s2022-swiss-1.2':"aOJgJ6wP4I"},
            'Halo':{'s2022-swiss-stage1':"pQwlhxUF78"},
            'League of Legends':{'s2022-swiss-reg':'dnC7l9AI-c'},
            'Call of Duty':{'s2022-swiss1':"JzP5Kj47A5"},
            'Chess':{'s2022-d1A':'CDYWEwBD4v','s2022-d1B':"HfvwaXxuTU",'s2022-d2A':"OAGZPjzmi6",'s2022-d2B':"f1nINKljXQ"},
            'Overwatch':{'s2022-groupD':"kHpVk1RCSR"},
            'CS:GO':{'s2022-swiss':"3xrGklEEpL"},
            'Apex Legends':{'s2022-reg':'dkw-z8ss9J'}
            }
        self.win_loss_cat = ['Rocket League','Valorant','Halo','League of Legends','Call of Duty','CS:GO','Overwatch']
        self.win_loss_tie_cat = ['Chess']
        self.grand_prix_cat = ['Apex Legends']
        
    @commands.command(aliases=['sb'],brief = 'Print Organizations Scoreboard')
    async def scoreboard(self, ctx, *, org):

        org_teams = dict()
        await ctx.send('Searching for: ' + org + '....')
        final_msg = str()
        for game in self.brackets.keys():
            print("Querying: " + game)
            org_teams[game] = list()
            for sub_bracket in self.brackets[game].values():
                teams = get_org_teams(self.endpoint, org,sub_bracket)
                for team in teams:
                    org_teams[game].append(team)

            def scoreboard_sorter(teams):
                newlist = sorted(teams,key=operator.itemgetter('rank'))
                return newlist

            scoreboard = scoreboard_sorter(org_teams[game])

            if game in self.grand_prix_cat:
                final_msg += '**---------' + game + ' (Grand Prix Scoring)------------**\n'
                
            elif game in self.win_loss_tie_cat:
                final_msg += '**---------' + game + ' (W-L-T)------------**\n'
                
            elif game in self.win_loss_cat:
                final_msg += '**---------' + game + ' (W-L)------------**\n'    

            if len(scoreboard) == 0: 
                final_msg += 'No teams found for ' + game + '\n'

            for team in scoreboard:
                if game in self.grand_prix_cat:
                    msg =  "**#" + str(team['rank'])  + "** - " + team['data']['dn'] + " - Points: " + str(team['data']['swiss_points']) + "\n"
                    final_msg += msg
                elif game in self.win_loss_tie_cat:
                    msg =  "**#" + str(team['rank'])  + "** - " + team['data']['dn'] + " (" + str(team['data']['wins']) + "-" + str(team['data']['losses']) + "-" + str(team['data']['ties'])+ ")\n"
                    final_msg += msg
                elif game in self.win_loss_cat:
                    msg =  "**#" + str(team['rank'])  + "** - " + team['data']['dn'] + " (" + str(team['data']['wins']) + "-" + str(team['data']['losses']) + ")\n"
                    final_msg += msg
    

        try:
            print(final_msg)
            await ctx.send(final_msg)
        except Exception as e:
            print('Error sending scoreboard result:')
            print (e)

def setup(bot):
    bot.add_cog(CeaCommands(bot))