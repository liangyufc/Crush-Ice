import platform
from os import system
import numpy as np
from math import inf
import time


HUMAN = 1
AI = -1
board = np.zeros(0)

def non_empty_cells(state, player):
    x, y = np.where(state == player)
    cells = np.c_[x, y]

    return cells

def wins(state, player):
    unique = np.unique(state)
    if player in unique:
        return False
    else:
        return True

def game_over(state):
    return wins(state, HUMAN) or wins(state, AI)

def valid_move(x, y, player):
    return np.any([np.array_equal(cell, [x, y]) for cell in non_empty_cells(board, player)])

def set_move(x, y, player):
    if valid_move(x, y, player):
        board[x, y] = 0
        return True
    else:
        return False

def render(state, c_choice, h_choice):
    # print the current board on the terminal
    chars = {
        -1: c_choice,
        +1: h_choice,
        0: ' '
    }
    print('\n' + '-' * (4 * board.shape[0] + 1))
    for row in state:
        print('|', end='')
        for cell in row:
            print(f' {chars[cell]} |', end='')
        print('\n' + '-' * (4 * board.shape[0] + 1))

def side_effect(state, move):

    x, y = move[0], move[1]
    removed_neighbors = []

    # valid neighbors
    neighbors = []
    if (x - 1) >= 0:
        if state[x-1, y] != 0:
            neighbors.append([x-1, y])
    if (x + 1) < state.shape[0]:
        if state[x+1, y] != 0:
            neighbors.append([x+1, y])
    if (y - 1) >= 0:
        if state[x, y-1] != 0:
            neighbors.append([x, y-1])
    if (y + 1) < state.shape[1]:
        if state[x, y+1] != 0:
            neighbors.append([x, y+1])

    # count number of 0 neighbors for each neighbor
    for neighbor in neighbors:
        i, j = neighbor[0], neighbor[1]
        count = 0
        if (i - 1) >= 0 and state[i-1, j] == 0:
            count = count + 1
        if (i + 1) < state.shape[0] and state[i+1, j] == 0:
            count = count + 1
        if (j - 1) >= 0 and state[i, j-1] == 0:
            count = count + 1
        if (j + 1) < state.shape[1] and state[i, j+1] == 0:
            count = count + 1
        if count > 1:
            state[i, j] = 0
            removed_neighbors.append([i, j])
    
    return state, removed_neighbors

def evaluate(state):
    return np.sum(state)

def minimax(state, player):

    depth = non_empty_cells(state, player).shape[0]

    if player == AI:
        best_move_score = [-1, -1, -inf]
    else:
        best_move_score = [-1, -1, +inf]

    if depth == 0 or game_over(state):
        score = evaluate(state)
        return [-1, -1, score]
    
    for cell in non_empty_cells(state, player):
        x, y = cell[0], cell[1]
        # print('\nBoard: {}'.format(board[x, y]))
        # print('If move [{}, {}]'.format(x,y))
        state[x, y] = 0
        # print('Board: {}'.format(board[x, y]))
        state, _ = side_effect(state, (x,y))
        if wins(state, AI):
            score = evaluate(state)
            best_move_score = [x, y, score]
            return best_move_score
        move_score = minimax(state, -player)
        state[x, y] = player
        move_score[0], move_score[1] = x, y

        if player == AI:
            if move_score[2] > best_move_score[2]:
                best_move_score = move_score
        else:
            if move_score[2] < best_move_score[2]:
                best_move_score = move_score
    
    return best_move_score



def ai_turn(c_choice, h_choice):

    global board
    depth = non_empty_cells(board, AI).shape[0]

    if depth == 0 or game_over(board):
        return
    
    # clean()
    print('\nAI pick ' + c_choice)
    render(board, c_choice, h_choice)

    if depth == 8:
        x, y = np.where(board == AI)
        cells = np.c_[x, y]
        move = cells[np.random.randint(cells.shape[0])]
    else:
        move = minimax(np.copy(board), AI)
    
    print('\nAI set move ({}, {})\n'.format(move[0] + 1, move[1] + 1))

    set_move(move[0], move[1], AI)
    board, removed_neighbors = side_effect(np.copy(board), (move[0], move[1]))

    for removed_n in removed_neighbors:
        print('Side efftect ({}, {})'.format(removed_n[0] + 1, removed_n[1] + 1))
    

def human_turn(c_choice, h_choice):

    global board
    depth = non_empty_cells(board, HUMAN).shape[0]
    if depth == 0 or game_over(board):
        return
    
    # clean()
    print('\nHuman pick ' + h_choice)
    render(board, c_choice, h_choice)

    move = [-1, -1]
    while any(m < 0 for m in move) or any(m > (board.shape[0]-1) for m in move):
        try:
            row = int(input('\nYour row (start from 1): '))
            col = int(input('Your col (start from 1): '))
            if valid_move(row - 1, col - 1, HUMAN):
                move = [row - 1, col - 1]
                set_move(move[0], move[1], HUMAN)
                board, removed_neighbors = side_effect(np.copy(board), (move[0], move[1]))
            else:
                print('Not valid move.')
        except (KeyError, ValueError):
            print('Not valid choice.')

    for removed_n in removed_neighbors:
        print('Side efftect ({}, {})'.format(removed_n[0] + 1, removed_n[1] + 1))

def clean():
    # clear the terminal
    os_name = platform.system().lower()
    if 'windows' in os_name:
        system('cls')
    else:
        system('clear')

def read_board_config(filename, c_choice, h_choice):
    lines = open(filename,'r').read().split('\n')
    n = int(lines[0])
    board = np.zeros((n, n))

    ints = {
        c_choice: -1,
        h_choice: +1
    }

    for i in range(1, len(lines)):
        line = lines[i].split(' ')
        for j in range(len(line)):
            board[i-1, j] = ints[line[j]]
    
    return board

if __name__ == '__main__':
    # clean()
    h_choice = '' # B or R
    c_choice = '' # B or R
    h_first = ''  # whether human plays first

    # Human chooses B or R
    while h_choice != 'B' and h_choice != 'R':
        try:
            print('')
            h_choice = input('Choose B or R.\nChosen: ').upper()
        except(KeyError, ValueError):
            print('Not valid choice.')
    
    if h_choice == 'B':
        c_choice = 'R'
    else:
        c_choice = 'B'
    
    clean()
    while h_first != 'Y' and h_first != 'N':
        try:
            h_first = input('First to start?[y/n]: ').upper()
        except (KeyError, ValueError):
            print('Not valid input.')

    # read board configuration
    board = read_board_config('test_n4.txt', c_choice, h_choice)

    # main game
    while (non_empty_cells(board, AI).size > 0 or non_empty_cells(board, HUMAN).size > 0) and not game_over(board):
        if h_first == 'N':
            ai_turn(c_choice, h_choice)
            h_first = ''

        human_turn(c_choice, h_choice)
        ai_turn(c_choice, h_choice)
    
    render(board, c_choice, h_choice)

    if wins(board, HUMAN) and not wins(board, AI):
        print('You win!')
    elif wins(board, AI) and not wins(board, HUMAN):
        print('You lose!')
    else:
        print('Draw!')