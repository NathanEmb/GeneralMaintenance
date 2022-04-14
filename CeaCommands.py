from discord.ext import commands
from RequestManager import get_org_teams
import operator

class CeaCommands(commands.Cog):
    def __init__(self,bot):

        self.bot = bot
        self.headers = {'User-Agent':'GM_Stats'}
        self.endpoint = {'url':'https://1ebv8yx4pa.execute-api.us-east-1.amazonaws.com/prod/','Header':self.headers}
        self.brackets = {
            'Rocket League':{'s2022-legacy':'vsrMjnFDMc','s2022-contenders':'WZaqjbfPLL','stage2':'tnhmjDEqaV'},
            'Valorant': {'s2022-swiss-1.2':"aOJgJ6wP4I"},
            'Halo':{'s2022-swiss-stage1':"pQwlhxUF78", "s2022-swiss-stage2":'pQwlhxUF78'},
            'League of Legends':{'s2022-swiss-reg':'dnC7l9AI-c'},
            'Call of Duty':{'s2022-swiss1':"JzP5Kj47A5"},
            'Chess':{'s2022-d1A':'CDYWEwBD4v','s2022-d1B':"HfvwaXxuTU",'s2022-d2A':"OAGZPjzmi6",'s2022-d2B':"f1nINKljXQ",'stage2':"fYaW2Lo9a9"},
            'Overwatch':{'stage2':'tYz4n7cDQ7'},
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
                teams = get_org_teams(self.endpoint, org, sub_bracket)
                for team in teams:
                    team_recorded = False

                    for existing_team in org_teams[game]:
                        if team['tid'] == existing_team['tid']:
                            team_id = team['tid']
                            existing_team[team_id]['wins'] += team[team_id]['wins']
                            existing_team[team_id]['losses'] += team[team_id]['losses']
                            existing_team[team_id]['ties'] += team[team_id]['ties']
                            team_recorded = True

                            if existing_team[team_id]['uts'] < team[team_id]['uts'] and team[team_id]['uts'] != '0000-00-00':
                                existing_team[team_id]['uts'] = team[team_id]['uts']
                                existing_team[team_id]['swiss_points'] = team[team_id]['swiss_points']
                                existing_team[team_id]['rank'] = team[team_id]['rank']
                        
                        
                    if team_recorded == False:
                        org_teams[game].append(team)
                        #else:
                            #org_teams[game].append(team)
                    #else:
                        #org_teams[game].append(team)

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
                team_id = team['tid']
                if game in self.grand_prix_cat:
                    msg =  "**#" + str(team['rank'])  + "** - " + team[team_id]['dn'] + " - Points: " + str(team[team_id]['swiss_points']) + "\n"
                    final_msg += msg
                elif game in self.win_loss_tie_cat:
                    msg =  "**#" + str(team['rank'])  + "** - " + team[team_id]['dn'] + " (" + str(team[team_id]['wins']) + "-" + str(team[team_id]['losses']) + "-" + str(team[team_id]['ties'])+ ")\n"
                    final_msg += msg
                elif game in self.win_loss_cat:
                    msg =  "**#" + str(team['rank'])  + "** - " + team[team_id]['dn'] + " (" + str(team[team_id]['wins']) + "-" + str(team[team_id]['losses']) + ")\n"
                    final_msg += msg
    
        try:
            print(final_msg)
            await ctx.send(final_msg)
        except Exception as e:
            print('Error sending scoreboard result:')
            print (e)

def setup(bot):
    bot.add_cog(CeaCommands(bot))