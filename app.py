import argparse
import uuid
import redis
import json
from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
import numpy as np
from utils import *


parser = argparse.ArgumentParser()
parser.add_argument("--host_redis_path", help="""pass redis host for docker
                    or for running standalone""", type=str, default="localhost")
# For docker give input as host.docker.internal
# This helps in running the file as standalone as well as using docker

args = parser.parse_args()
host_redis_path = args.host_redis_path
# redis calls
redis_db = redis.Redis(host=host_redis_path, port=6379, db=0)
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


""" The User is the landing page where player id sessions would be set for
all the users.
"""
@app.route('/user', methods=['GET'])
def user():
    if 'player_id' not in session:
        session['player_id'] = str(uuid.uuid1())  # creates unique sessions
    return render_template('multi-forms.html')


""" Creates gameID. Here by default player 1 's information is stored.
Other game details are also created
"""
@app.route('/generate', methods=['POST'])
def generate():
    if request.form['name'] != '':
        gameID = str(uuid.uuid4())
        # create game dictionary which is stored in redis
        game_redis = {
            'players': { # stores 2 players
                session['player_id']: {
                    'username': request.form['name'],
                    'turn': 1,
                    'winrule': [1, 1, 1, 1, 1] # default for player 1
                    }
                },
            'players_counter': 1, # overall  only 2 players allowed to register
            'turn_counter': 1, # used to decide turns
            'game_state': np.zeros(shape=(6, 9)).tolist(), # 6 rows 9 columns
            'game_end':'No', # if game ends, states are frozen
            'game_winner': '',
            'game_loser': '',
            'column_blocks': [] # if any column fills up
                }
        # unique game ID as key, value is player and game information
        redis_db.set(gameID, json.dumps(game_redis))
        return render_template('player1.html', name=request.form['name'], gameID=gameID)
    else:
        return redirect(url_for('user'))

""" Player 2 s information is stored. This is from the player who enters into the game using gameID.
"""
@app.route('/start', methods=['POST'])
def start():
    if request.form['name'] != '':
        # check gameID exists
        if redis_db.exists(request.form['gameID']):
            # gets gameinfo stored in gameID from redis
            game_redis = json.loads(redis_db.get(request.form['gameID']))
            # checking if we can register another player
            if game_redis['players_counter'] < 2:
                game_redis['players'][session['player_id']] = {
                    'username':request.form['name'],
                    'turn':2,
                    'winrule':[2, 2, 2, 2, 2]   # for player2 its 2 for winning
                    }
                game_redis['players_counter'] = 2
                redis_db.set(request.form['gameID'], json.dumps(game_redis))
                return render_template_string('''<h3> Your gameID is {{gameID}}</h3>
                      <a href="{{ url_for('game_state',gameID=gameID) }}"> 
                       Click here </a> to go to game state ''', gameID=request.form['gameID'])
            # by chance a user reenters despite being registered
            elif session['player_id'] in game_redis['players'].keys():
                return render_template_string('''<h3> Your gameID is {{gameID}}</h3>
                      <a href="{{ url_for('game_state',gameID=gameID) }}"> 
                       Click here </a> to go to game state ''', gameID=request.form['gameID'])
            else: # if 3rd players tries to register
                return 'There are already 2 players. Please create another ID'
        else:
            return 'ID does not exists '
    else: # ensuring some name is entered
        return redirect(url_for('user'))

"""
Multiple game servers can be created and the game be played at same time.
Unique game state information gets stored in redis. This is default page for game state
"""
@app.route('/game_state/<gameID>', methods=['GET', 'POST'])
def game_state(gameID):
    if redis_db.exists(str(gameID)):
        game_redis = json.loads(redis_db.get(gameID))
        if game_redis['game_end'] == 'No': # check game in on
            if game_redis['players_counter'] == 2: # ensure only 2 player enters
                if (game_redis["players"][session['player_id']]["turn"] ==
                        game_redis["turn_counter"]): # turn condition to check who will play
                    return render_template('game_state_player1.html',
                                           your_list=game_redis['game_state'], error_message='',
                                           gameID=gameID)
                else: # shown to other player for waiting
                    return render_template('game_state_player_wait.html',
                                           your_list=game_redis['game_state'], error_message='',
                                           gameID=gameID)
            else:
                return render_template_string('''<h2>Waiting for player 2 </h2>
                <a href="{{ url_for('game_state',gameID=gameID) }}">  'Check here' </a>''',
                                              gameID=gameID)
        else: # end state
            return 'the game ended. Winner is '+game_redis['game_winner'] +' and loser is '+ game_redis['game_loser']
    else: # bychance someone tries to enter directly with wrong ID
        return render_template_string('''<h2>The ID you entered is not in our database </h2>
                <p>To go to main page. Click</p> 
                <a href="{{ url_for('game_state',gameID=gameID) }}"> 'Main Page'</a>''',
                                      gameID=gameID)


"""
This post requests helps in making a move. After making the move user would always be redirected to game state API.
"""
@app.route('/gamepost/<gameID>', methods=['POST'])
def gamepost(gameID):
    game_redis = json.loads(redis_db.get(gameID))
    move = request.form['number']
    try:
        move = int(move)
    except ValueError:
        error_text = 'please enter integer values only'
        return render_template('game_state_player1.html', your_list=game_redis['game_state'],
                               error_message=error_text, gameID=gameID)
    if move >= 9 or move < 0:
        error_text = 'please enter numbers only between 0 and 8'
        return render_template('game_state_player1.html', your_list=game_redis['game_state'],
                               error_message=error_text, gameID=gameID)

    if move in game_redis['column_blocks']:
        # checks if any column is full
        error_text = 'please select another column'
        return render_template('game_state_player1.html', your_list=game_redis['game_state'],
                               error_message=error_text, gameID=gameID)

    if len(game_redis['column_blocks']) == 9:
        # if game is tied where all columns are full
        game_redis['game_end'] = 'Yes'
        game_redis['game_winner'] = 'Tie'
        game_redis['game_loser'] = 'Tie'
        redis_db.set(gameID, json.dumps(game_redis))
        return 'The game is a Tie'
    # temp game state is numpy array
    temp_game_state, game_redis['column_blocks'] = condition(np.array(game_redis['game_state']),
                                                             move, game_redis["turn_counter"],
                                                             game_redis['column_blocks'])
    row, column, diagonal = update(temp_game_state)
    game_redis['game_state'] = temp_game_state.tolist()

    winrule = game_redis['players'][session['player_id']]['winrule']
    if winrule in row or winrule in column.tolist() or winrule in diagonal:
        game_redis = winner_rule(game_redis, session['player_id'])
        redis_db.set(gameID, json.dumps(game_redis))
        # redirect ensures there's no cache even if you click back
        return redirect(url_for('game_state', gameID=gameID))
    # change turn    
    if game_redis['turn_counter'] == 1:
        game_redis['turn_counter'] = 2
    elif game_redis['turn_counter'] == 2:
        game_redis['turn_counter'] = 1

    redis_db.set(gameID, json.dumps(game_redis))
    return redirect(url_for('game_state', gameID=gameID))


"""
To quit game
"""
@app.route('/quit/<gameID>', methods=['GET', 'POST'])
def quit(gameID):
    game_redis = json.loads(redis_db.get(gameID))
    game_redis = quit_rule(game_redis, session['player_id'])
    redis_db.set(gameID, json.dumps(game_redis))
    return redirect(url_for('game_state', gameID=gameID))


@app.route('/master_reset', methods=['GET', 'POST'])
def master_reset():
    if request.method == 'POST':
        if request.form['delete'] == 'delete':
            redis_db.flushall()
            return 'Master reset is successful. All gameIDs deleted from database'
    return render_template('master_delete.html')


def create_app():
    # used for testing
    return app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
