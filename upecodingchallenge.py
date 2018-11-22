#!/usr/bin/python

import requests, json, time

base_url = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/"
headers = {'content-type': 'application/x-www-form-urlencoded'}

# Get access token to start the session
session_url = base_url + "session"
session_data =  { 'uid': '004963466' }
r = requests.post(session_url, session_data, headers)
ACCESS_TOKEN = json.loads(r.text)["token"]

# Return the current location of the player
def get_start_location():
    r = requests.get(game_url, headers)
    return json.loads(r.text)["current_location"]

# Return the maze size and game status
def get_game_states():
    r = requests.get(game_url, headers)
    game_state = json.loads(r.text)
    return (game_state["maze_size"], game_state["status"])

# Find the new location if a move was to be done
def calculate_location(x, y, move):
    if move == "UP":
        return (x, y-1)
    if move == "DOWN":
        return (x, y+1)
    if move == "LEFT":
        return (x-1, y)
    if move == "RIGHT":
        return (x+1, y)

# Perform an action and return the result of the move
def do_move(move):
    game_data = {'action': move}
    r = requests.post(game_url, game_data, headers)
    return json.loads(r.text)["result"]

# Solve a level of the maze using recursion
def solve_level(vertex):
    x = vertex[0]
    y = vertex[1]
    if visited[x][y] == 0:
        visited[x][y] = 1
        for move in moves:
            (a, b) = calculate_location(x, y, move)
            if a > -1 and a < maze_size[0] and b > -1 and b < maze_size[1] and visited[a][b] == 0:
                move_result = do_move(move)
                if move_result == "OUT_OF_BOUNDS" or move_result == "WALL":
                    visited[a][b] = 1
                if move_result == "END":
                    return True
                if move_result == "SUCCESS":
                    if solve_level((a, b)):
                        return True
                    else:
                        do_move(reverse_move[move])
        return False
    return False

# Set up game url to obtain game states and move results
game_url = base_url + "game?token=" + ACCESS_TOKEN
(maze_size, game_status) = get_game_states()
game_level = 1

moves = ["UP", "DOWN", "LEFT", "RIGHT"]
reverse_move = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT"
}

print "Time to Complete Each Level"
print "---------------------------"

# Execute loop until all levels of the maze are complete
while game_status != "FINISHED":
    start_time = time.time()
    visited = [[0 for i in range(maze_size[1])] for j in range(maze_size[0])]
    solve_level(get_start_location())
    (maze_size, game_status) = get_game_states()
    if game_status == "GAME_OVER" or game_status == "NONE":
        print "Failed :/"
        break
    print "Level %d: %s s" %(game_level, (time.time() - start_time))
    game_level += 1

if game_status == "FINISHED":
    print "SUCCESS :)"
