from genericpath import exists
import requests


def get_org_teams(endpoint, org, bracket):
    #Take org (string) and find all teams in a given bracket (string)
    bracket_url = endpoint['url']+'brackets/'+ bracket
    scoreboard_url = endpoint['url']+'brackets/'+ bracket + "/scoreboard"
    bracket_req= requests.get(bracket_url, headers=endpoint['Header'])
    scoreboard_req = requests.get(scoreboard_url, headers=endpoint['Header'])

    bracket_dict = bracket_req.json()
    scoreboard_dict = scoreboard_req.json()

    team_summary = bracket_dict['data'][0]['ts']
    scoreboard_data = scoreboard_dict['data']['rs']
    org_teams = list()

    for team_dict in team_summary:
        if team_dict['org'].lower() == org.lower():
            team_wins = int()
            team_loss = int()
            team_rank = int()
            team_tie = 0
            for team in scoreboard_data:
                if team['tid'] == team_dict['tid']:
                    team_score = team['s']
                    team_wins = team['w']
                    team_loss = team['l']
                    if 't' in team.keys():
                        team_tie = team['t']
                    team_rank = team['r']

            temp_dict = {'rank':team_rank}   
            temp_dict['data'] ={
            'dn':team_dict['dn'],
            'tid':team_dict['tid'],
            'org':team_dict['org'],
            'swiss_points':team_score,
            'wins':team_wins,
            'losses':team_loss,
            'ties':team_tie,
            'rank':team_rank    
            }

            org_teams.append(temp_dict)
            
    
    return org_teams

def get_team_results(endpoint, team, bracket):
    #return results of team in bracket
    url = endpoint['url']+'brackets/'+ bracket
    bracket_json = requests.get(url, headers=endpoint['Header'])
    bracket_dict = bracket_json.json()

    round_data = bracket_dict['data'][0]['rounds']
    team_results = list()

    for i,round in enumerate(round_data):
        for match in round['matches']:
            if len(match['ts'])==2:
                team1 = match['ts'][0]['dn']
                team1_score = match['ts'][0]['s']
                team2 = match['ts'][1]['dn']
                team2_score = match['ts'][1]['s']

            else:
                team1 = match['ts'][0]['dn']
                team1_score = 0
                team2 = 'BYE WEEK'
                team2_score = 0

            if team.lower() == team1.lower() or team.lower() == team2.lower():
                team_results.append(
                {
                'week_num':(i+1),
                'team1':team1, 
                'team1_score':team1_score, 
                'team2':team2, 
                'team2_score':team2_score 
                })
    
    return team_results


            