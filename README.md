# Installation

Redis is required for holding game states.

### Running Redis container

```
docker run  --rm  -p 6379:6379 --name redis-server redis
```

We can run the connect-5 game either as standalone or using docker container.


### Run using Docker

```
docker build -t connect5 .
docker run --rm -p 7000:7000  connect5 --host_redis_path host.docker.internal
```

### Run as standalone

Python 3.7 is used

For installing requirements.

```
pip3 install -r requirements.txt
```

#### To Run the Code
```
python3 app.py
```

# User Instructions
To get started.
Go to the following page on your web browser
```
http://localhost/7000/user
```

- Create a Game ID if you are a new player.
- Once after recieving the ID share it with your friend with whom you want to play.
- The second player needs to enter the same Game ID
- Once both players have entered the ID you would get directed to game page
- Every player gets a chance to play alternatively. Player 1 is by default '1' and Player 2 is by default '2'. The initial game state would be all zeros. Every addition on column would replace the numbers from the bottom

There is an option 'Quit' for users to quit the game anytime in between.
To delete all the data from redis container
Go to
```
http://localhost:7000/master_reset
```
and type 'delete'


#  Testing
Pytest-flask is used for testing.
```
pip3 install pytest
pip3 install pytest-flask
```
To simply run the tests
```
py.test
```


# Further Documentation


- Arguments were used so that the same code can run as standalone or with docker.
- User API contains multiform which directs players either to start or Generate.
- Start API is for player1 for entering his details as well as it creates gameID and pushes ito Redis, while generate API edits player2 details and gives a go-ahead for the game to be started in game state API.
- The game_state API is unique since we can create multiple game ID's. It can support multiple players playing at same time and all its game state information gets stored in Redis DB.
- The state of the game is maintained within game_state API while gamepost makes the move for the players.
- Redirects had been created in order to avoid Cache. The design choices were made in viewpoint of scaling.
- Testing is done using py-test flask.
- Frontend will show all zeros as initial game starting point. 1's and 2's placed on respective places as game progresses.

## File Information

- **utils.py** holds the logic functions of the game.
- **conftest.py** is used for pytest-flask.
- Templates folder has htmls for relevant API's while test folder has test cases

## Dictionary structure
This is how redis dictionary structure looks which holds the game logic.

Players also get unique ID's.

```
{'players': {'1ff0effa-b333-11ea-8e55-0242ac110003':
{'username':'player1', 'turn': 1, 'winrule': [1, 1, 1, 1, 1]},
  '054c3218-b3b0-11ea-8aad-0242ac110003':
    {'username': 'player2', 'turn': 2, 'winrule': [2, 2, 2, 2, 2]}},
    'players_counter': 2,
    'turn_counter': 1,
    'game_state': [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]],
    'game_end': 'Yes',
    'game_winner': 'player1',
    'game_loser': 'player2', 'column_blocks': []}


    ```
