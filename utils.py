import numpy as np
"""
just checks the winning rule and sets winner/losers
"""
def winner_rule(game_redis,player_id):
    # just to get the other key
    for i in game_redis['players'].keys():
        if player_id!=i:
            loser=i
    winner = game_redis['players'][player_id]['username']
    game_redis['game_winner'] = winner
    game_redis['game_loser'] = game_redis['players'][loser]['username']
    game_redis['game_end'] = 'Yes'
    return game_redis


"""
quitting rulw
"""
def quit_rule(game_redis,player_id):
    loser = game_redis['players'][player_id]['username']
    for i in game_redis['players'].keys():
        if player_id!=i:
            winner=i

    game_redis['game_winner'] = game_redis['players'][winner]['username']
    game_redis['game_loser'] = loser
    game_redis['game_end'] = 'Yes'
    return game_redis


'''
Get all diagonals
'''
def diagonals(array):    
    diags = [array[::-1,:].diagonal(i) for i in range(-array.shape[0]+1,array.shape[1])]

    # Now back to the original array to get the upper-left-to-lower-right diagonals,
    # starting from the right, so the range needed for shape (x,y) was y-1 to -x+1 descending.
    diags.extend(array.diagonal(i) for i in range(array.shape[1]-1,-array.shape[0],-1))
    
    filtered = list(filter(lambda x:len(x)>4,diags)) # x>4 for connect5

    all_diags = [n.tolist() for n in filtered]
    diagonal_list = []
    for i in range(len(all_diags)):
        if len(all_diags[i])>5:
            diagonal_list.append(all_diags[i][1:])
            diagonal_list.append(all_diags[i][:-1])
        else:
            diagonal_list.append(all_diags[i])
    return diagonal_list

def columns(array):
    n = 5 # since its connect-5

    temp = []
    for j in range(len(array)):
        for i in range(len(array)-(n-1)):       
            temp.append(array[i:i+n,j])
    column_list = np.array(temp) # gets all columns for connect5
    return column_list

def rows(array):
    n = 5
    row_list = []
    width = 9
    # gets all rows in set of 5 to check the winner
    for i in range(len(array)):
        for j in range(width-(n-1)):
            row_list.append(array[i,j:j+n].tolist())
    return row_list 

def update(array):
    return rows(array), columns(array), diagonals(array)

'''
Updates the matrix. Checks if a column is full 
'''
def condition(matrix, player_name_selection, player_index, column_block):
    row_index = 0
    for index,i in enumerate(matrix[:, player_name_selection]):
        if i != 0:
            if index == 1:
                column_block.append(player_name_selection)
            break
        row_index = row_index+1     
    matrix[row_index-1][player_name_selection] = player_index
    
    return matrix, column_block
