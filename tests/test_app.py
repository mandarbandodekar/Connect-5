import pytest
from flask import url_for
from flask import session
import redis 
import json 
import numpy as np
from utils import diagonals
from utils import  winner_rule
redis_db = redis.Redis(host='localhost', port=6379, db=0)
mock_redis_object = 'mock_object'
mock_data =  {'players':{
                    'mock_player':{
                            'username': 'mock_player',
                            'turn':999,
                            'winrule':[9,9,9,9,9]
                            },
                    'mock_2':{'username': 'mock_player_2',
                            'turn':2999,
                            'winrule':[29,29,29,29,29]}
                        },
                'players_counter':0,
                'turn_counter':0,
                'game_state':'',
                'game_end':'',
                'game_winner':'',
                'game_loser':'',
                'column_blocks':[]
                }
 
redis_db.set(mock_redis_object,json.dumps(mock_data))

def test_status(client):
    ## test to check whether flask webform is online
    res = client.get(url_for('user'))
    assert res.status_code == 200

def test_value_set_in_session(client):
    client.get(url_for('user'))
    assert 'player_id' in session

def test_game_set(client):
    res = client.post(url_for('game_state',gameID='mock_object'))
    assert res.status_code == 200

def test_generate(client):
    res = client.post(url_for('game_state',gameID='mock_object',name='Mock'))
    assert res.status_code == 200

def test_winner_rule():
    obj = json.loads(redis_db.get('mock_object'))
    game_redis = winner_rule(obj,'mock_2')
    assert game_redis['game_end']== 'Yes'

def test_quit(client):
    res = client.post(url_for('quit',gameID='mock_object')) 
    assert res.status_code == 500

def test_diagonal():
    mock_array = np.array([[1,2,3,4,5],
                     [6,7,8,9,10],
                     [11,12,13,14,15],
                     [16,17,18,19,20],
                    [21,22,23,24,25]])  
    answer_recieved = diagonals(mock_array)
    expected_answer = [[21, 17, 13, 9, 5], [1, 7, 13, 19, 25]]

    assert answer_recieved == expected_answer
