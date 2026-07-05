import curses

# Core Settings
TIC_TIMEOUT = 0.1
PANEL_HEIGHT = 3

# Visual Assets & Environment
NUM_STARS = 100
STAR_SYMBOLS = "+*.:⁕◦"
EXPLOSION_FRAMES = [
    "           (_)\n       (  (   (  (\n      () (  (  )\n        ( )  ()",
    "           (_)\n       (  (   (\n         (  (  )\n          )  (",
    "            (\n          (   (\n         (     (\n          )  (",
    "            (\n              (\n            ("
]

# Game Lore & UI
PLASMA_GUN_YEAR = 2020
GAMEOVER_FRAME = """
   _____                         ____                 
  / ____|                       / __ \                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \ / _ \ | |  | \ \ / / _ \ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\ V /  __/ |   
  \_____|\__,_|_| |_| |_|\___|  \____/  \_/ \___|_|
"""
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: "ISS start building",
    2011: "Messenger launch to Mercury",
    2020: "Take the plasma gun! Shoot the garbage!",
}

# Gameplay & Balance
SHIP_SPEED = 6.0
VERTICAL_SHOT_SPEED = -1.5
HORIZONTAL_SHOT_SPEED = 0
OBSTACLE_SPEED = 0.2

# Keybindings
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = curses.KEY_LEFT
RIGHT_KEY_CODE = curses.KEY_RIGHT
UP_KEY_CODE = curses.KEY_UP
DOWN_KEY_CODE = curses.KEY_DOWN
