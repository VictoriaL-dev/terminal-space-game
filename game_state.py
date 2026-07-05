coroutines = []
obstacles = []
obstacles_in_last_collisions = []
game_over = False
year = 1957


def reset():
    global coroutines, obstacles, obstacles_in_last_collisions, game_over, year
    coroutines.clear()
    obstacles.clear()
    obstacles_in_last_collisions.clear()
    game_over = False
    year = 1957
