# Game Engine & Timing
TIC_TIMEOUT = 0.1
OBSTACLE_DELAY_RANGE = (8, 20)

# Cosmos & Environment
NUM_STARS = 100
STAR_SYMBOLS = "+*.:⁕◦"

# Physics & Movement
SHIP_SPEED = 6.0
VERTICAL_SHOT_SPEED = -1.5
HORIZONTAL_SHOT_SPEED = 0
OBSTACLE_SPEED = 0.2

# Controls & Keybindings
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

# Global Game State
coroutines = []
obstacles = []
obstacles_in_last_collisions = []
