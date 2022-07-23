import berserk
import pandas as pd
import numpy as np


# filtering the data
# filtering games played with stockfich
def filter_stockfish(games):
    games1=[]
    for i in games:
        try :
            i['players']['black']['user']['id']
            i['players']['white']['user']['id']
            games1.append(i)
        except (AttributeError,KeyError):
            continue
    return games1
# filtering games doesn't start
def filter_incomplete_games(games):
    games1=[]
    for i in games:
        try :
            i['opening']['name']
            games1.append(i)

        except (AttributeError,KeyError):
            continue
    return games1

    
def main(max_games,API_TOKEN='lip_3gD7WOiSA33fLaJoSojZ'):
    session = berserk.TokenSession(API_TOKEN)
    client = berserk.Client(session=session)
    games = list(client.games.export_by_player('yaS1Sine',max=max_games, 
     moves=False, tags=False, evals=True, opening=True))
    # keep only blitz and rapid games
    games=[i for i in games if (i['perf']=='blitz' or i['perf']=='rapid' or i['perf']=='bullet') and i['variant']=='standard']
    games=filter_stockfish(games)
    games=filter_incomplete_games(games)
    rating=[]
    color=[]
    opponent_rating=[]
    opening=[]
    Date=[]
    game_id=[]
    speed=[]
    game_ending=[]
    winner=[]
    tournament=[]
    accuracy=[]
    inaccuracy=[]
    mistake=[]
    blunder=[]
    analysis=[]
    for i in games:
        Date.append(i['createdAt'].strftime('%m/%d/%Y'))
        game_id.append(i['id'])
        speed.append(i['speed'] )
        game_ending.append(i['status'])
        opening.append(i['opening']['name'])
        if i['players']['black']['user']['id']=='yas1sine':
            color.append('black')
            rating.append(i['players']['black']['rating'])
            opponent_rating.append(i['players']['white']['rating'])

        if i['players']['white']['user']['id']=='yas1sine':
            color.append('white')
            rating.append(i['players']['white']['rating'])
            opponent_rating.append(i['players']['black']['rating'])
        if 'winner' in i:
            winner.append(i['winner'])
        else:
            winner.append(np.nan)
        if 'tournament' in i:
            tournament.append(True)
        else:
            tournament.append(False)
        if 'analysis' in i:

            # analysis
            cpl=''
            eval=i['analysis']
            for j in eval:
                if type(j)==dict:
                    if 'eval'in j:
                        cpl+=str(j['eval'])+' '
            analysis.append(cpl)

            if i['players']['black']['user']['id']=='yas1sine':
                accuracy.append(i['players']['black']['analysis']['acpl'])
                inaccuracy.append(i['players']['black']['analysis']['inaccuracy'])
                mistake.append(i['players']['black']['analysis']['mistake'])
                blunder.append(i['players']['black']['analysis']['blunder'])

            else:
                accuracy.append(i['players']['white']['analysis']['acpl'])
                inaccuracy.append(i['players']['white']['analysis']['inaccuracy'])
                mistake.append(i['players']['white']['analysis']['mistake'])
                blunder.append(i['players']['white']['analysis']['blunder'])
        else:
            analysis.append(np.nan)
            accuracy.append(np.nan)
            inaccuracy.append(np.nan)
            mistake.append(np.nan)
            blunder.append(np.nan)
    data={'game_id':game_id,
      'Date':Date,
      'tournament':tournament,
      'speed':speed,
      'opening':opening,
      'color':color,
      'rating':rating,
      'opponent_rating':opponent_rating,
      'game_ending':game_ending,
      'winner':winner,
      'analysis':analysis,
      'accuracy':accuracy,
      'inaccuracy':inaccuracy,
      'mistake':mistake,
      'blunder':blunder}
    pd.DataFrame(data).to_csv('data/games.csv', index=False)




if __name__ == "__main__":

    main(2000,API_TOKEN='lip_3gD7WOiSA33fLaJoSojZ')