import random
import curses
import asyncio
import itertools

import game_state, game_config
from obstacles import Obstacle
from physics import update_speed
from controls import read_controls
from curses_tools import draw_frame, get_frame_size


async def sleep(tics=1):
    """Pauses the coroutine execution for a specified number of game ticks.

    Args:
        tics (int): The number of game ticks to wait. Defaults to 1.
    """
    for _ in range(int(tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol, offset_tics):
    """Animates a single star blinking at a fixed coordinate.

    Args:
        canvas: A curses window object where the star will be drawn.
        row (int): The vertical coordinate (Y) on the canvas.
        column (int): The horizontal coordinate (X) on the canvas.
        symbol (str): The character representing the star.
        offset_tics (int): The number of initial game loop ticks to wait before
            starting the main blinking cycle. Used to desynchronize stars.

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    await sleep(tics=offset_tics)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(tics=20)

        canvas.addstr(row, column, symbol)
        await sleep(tics=3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(tics=5)

        canvas.addstr(row, column, symbol)
        await sleep(tics=3)


def get_star_coroutines(canvas, canvas_height, canvas_width):
    """Generates a list of coroutines representing randomly distributed stars.

    Args:
        canvas: A curses window object where the stars will be drawn.
        canvas_height (int): The maximum vertical dimension (height) of the canvas.
        canvas_width (int): The maximum horizontal dimension (width) of the canvas.

    Returns:
        list: A list of initialized coroutine objects.
    """
    coroutines = []

    for _ in range(game_config.NUM_STARS):
        row = random.randint(1, canvas_height - 2)
        column = random.randint(1, canvas_width - 2)
        symbol = random.choice(game_config.STAR_SYMBOLS)
        offset = random.randint(1, 30)

        coroutine = blink(canvas=canvas, row=row, column=column, symbol=symbol, offset_tics=offset)
        coroutines.append(coroutine)
    return coroutines


async def fire(canvas, start_row, start_column, rows_speed, columns_speed=0):
    """Animates a shot firing, flying across the screen, and hitting obstacles.

    Args:
        canvas: A curses window object where the shot will be drawn.
        start_row (int): The initial vertical coordinate (Y) for the shot.
        start_column (int): The initial horizontal coordinate (X) for the shot.
        rows_speed (float): Vertical speed per tick. Negative moves up,
            positive moves down.
        columns_speed (float): Horizontal speed per tick. Negative
            moves left, positive moves right. Defaults to 0.

    Returns:
        None: The coroutine finishes and returns when the shot moves
            off-screen, hits a border, or strikes an obstacle.
    """
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed
    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in game_state.obstacles:
            if obstacle.has_collision(row, column, obj_size_rows=1, obj_size_columns=1):
                game_state.obstacles_in_last_collisions.append(obstacle)

                center_row = obstacle.row + obstacle.rows_size / 2
                center_column = obstacle.column + obstacle.columns_size / 2

                explosion_coroutine = explode(canvas=canvas, center_row=center_row, center_column=center_column)
                game_state.coroutines.append(explosion_coroutine)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, frames):
    """Animates the player's spaceship and manages its controls and movement.

    Args:
        canvas: A curses window object where the spaceship will be drawn.
        start_row (int): The initial vertical coordinate (Y) for the spaceship.
        start_column (int): The initial horizontal coordinate (X) for the spaceship.
        frames (list of str): A list of multiline strings representing the
            ASCII art animation frames of the spaceship.

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    row, column = start_row, start_column
    canvas_height, canvas_width = canvas.getmaxyx()
    game_height, game_width = canvas_height - game_config.PANEL_HEIGHT, canvas_width

    ship_sizes = [get_frame_size(frame=frame) for frame in frames]
    ship_height = max([size[0] for size in ship_sizes])
    ship_width = max([size[1] for size in ship_sizes])

    duplicated_frames = [frame for frame in frames for _ in range(2)]
    frames_cycle = itertools.cycle(duplicated_frames)

    row_speed, column_speed = 0.0, 0.0

    for current_frame in frames_cycle:
        for obstacle in game_state.obstacles:
            if obstacle.has_collision(row, column, obj_size_rows=ship_height, obj_size_columns=ship_width):
                game_state.game_over = True

                center_row = row + ship_height / 2
                center_column = column + ship_width / 2

                game_state.coroutines.append(explode(canvas=canvas, center_row=center_row, center_column=center_column))
                game_state.coroutines.append(show_gameover(canvas=canvas))
                return

        rows_direction, columns_direction, space_pressed = read_controls(canvas=canvas)

        if space_pressed and game_state.year >= game_config.PLASMA_GUN_YEAR:
            shot_row = row
            shot_column = column + (ship_width // 2)

            shot_coroutine = fire(
                canvas=canvas,
                start_row=shot_row,
                start_column=shot_column,
                rows_speed=game_config.VERTICAL_SHOT_SPEED
            )
            game_state.coroutines.append(shot_coroutine)

        row_speed, column_speed = update_speed(
            row_speed=row_speed,
            column_speed=column_speed,
            rows_direction=rows_direction,
            columns_direction=columns_direction,
            row_speed_limit=game_config.SHIP_SPEED,
            column_speed_limit=game_config.SHIP_SPEED,
            fading=0.8
        )

        next_row = row + row_speed
        next_column = column + column_speed

        row = max(0, min(next_row, game_height - ship_height))
        column = max(1, min(next_column, game_width - ship_width - 1))

        if row in (0, game_height - ship_height): row_speed = 0.0
        if column in (1, game_width - ship_width - 1): column_speed = 0.0

        draw_frame(canvas=canvas, start_row=row, start_column=column, frame=current_frame)
        await asyncio.sleep(0)
        draw_frame(canvas=canvas, start_row=row, start_column=column, frame=current_frame, negative=True)


async def explode(canvas, center_row, center_column):
    """Animates an explosion effect at the specified coordinates.

    Args:
        canvas: The curses window object where the animation is drawn.
        center_row (int or float): The vertical center coordinate (row) of the explosion.
        center_column (int or float): The horizontal center coordinate (column) of the explosion.

    Returns:
        None: This coroutine does not return a value.
    """
    frame_rows, frame_columns = get_frame_size(frame=game_config.EXPLOSION_FRAMES[0])
    corner_row = center_row - frame_rows / 2
    corner_column = center_column - frame_columns / 2

    curses.beep()

    for frame in game_config.EXPLOSION_FRAMES:
        draw_frame(canvas=canvas, start_row=corner_row, start_column=corner_column, frame=frame)
        await asyncio.sleep(0)

        draw_frame(canvas=canvas, start_row=corner_row, start_column=corner_column, frame=frame, negative=True)
        await asyncio.sleep(0)


async def fly_garbage(canvas, column, frame, obstacle_speed):
    """Animates a single piece of garbage falling from the top to the bottom.

    Args:
        canvas: A curses window object where the garbage will be rendered.
        column (int): The fixed horizontal coordinate (X) where the garbage falls.
        frame (str): A multiline string containing the ASCII art for the garbage.
        obstacle_speed (float): The vertical distance (rows) the garbage travels per tick.

    Returns:
        None: This coroutine terminates when the garbage goes off-screen.
    """
    rows_number, columns_number = canvas.getmaxyx()
    obstacle_height, obstacle_width = get_frame_size(frame=frame)

    column = max(0, min(column, columns_number - obstacle_width - 1))
    row = 0
    max_row = (rows_number - game_config.PANEL_HEIGHT) - obstacle_height

    obstacle = Obstacle(row=row, column=column, rows_size=obstacle_height, columns_size=obstacle_width)
    game_state.obstacles.append(obstacle)

    try:
        while row < max_row:
            if obstacle in game_state.obstacles_in_last_collisions:
                game_state.obstacles_in_last_collisions.remove(obstacle)
                return

            draw_frame(canvas=canvas, start_row=row, start_column=column, frame=frame)
            await asyncio.sleep(0)
            draw_frame(canvas=canvas, start_row=row, start_column=column, frame=frame, negative=True)

            row += obstacle_speed
            obstacle.row = row
            obstacle.column = column
    finally:
        if obstacle in game_state.obstacles:
            game_state.obstacles.remove(obstacle)


def get_garbage_delay_tics(year):
    """Calculates the spawn delay for space garbage based on the game year.

    Args:
        year (int): The current calendar year of the game simulation.

    Returns:
        int or None: The number of game ticks to wait between spawns.
            Returns None if the year is before 1961, meaning no garbage
            should spawn at all.
    """
    if year < 1961: return None
    elif year < 1969: return 20
    elif year < 1981: return 14
    elif year < 1995: return 10
    elif year < 2010: return 8
    elif year < 2020: return 6
    return 2


async def fill_orbit_with_garbage(canvas, frames):
    """Continuously spawns garbage at the top of the canvas.

    Args:
        canvas: A curses window object where garbage tasks are deployed.
        frames (list of str): A list containing various ASCII art frames
            used to represent different garbage items.

    Returns:
        None: This coroutine runs infinitely.
    """
    rows, columns = canvas.getmaxyx()

    while True:
        if game_state.game_over:
            return

        delay_tics = get_garbage_delay_tics(year=game_state.year)
        if delay_tics is None:
            await asyncio.sleep(0)
            continue

        random_frame = random.choice(frames)
        obstacle_height, obstacle_width = get_frame_size(frame=random_frame)

        max_column = columns - obstacle_width - 1
        random_column = random.randint(1, max(1, max_column))

        garbage_coroutine = fly_garbage(
            canvas=canvas,
            column=random_column,
            frame=random_frame,
            obstacle_speed=game_config.OBSTACLE_SPEED
        )
        game_state.coroutines.append(garbage_coroutine)

        await sleep(tics=delay_tics)


async def show_gameover(canvas):
    """Displays the 'Game Over' ASCII art in the center of the screen.

    Args:
        canvas: A curses window object where the ASCII art will be rendered.

    Returns:
        None: This coroutine runs indefinitely once triggered, maintaining the game over
            screen until the application is closed.
    """
    canvas_height, canvas_width = canvas.getmaxyx()

    frame = game_config.GAMEOVER_FRAME
    frame_rows, frame_columns = get_frame_size(frame=frame)

    max_height = canvas_height - game_config.PANEL_HEIGHT
    start_row = (max_height // 2) - (frame_rows // 2)
    start_column = (canvas_width // 2) - (frame_columns // 2)

    while True:
        draw_frame(canvas=canvas, start_row=start_row, start_column=start_column, frame=frame)
        await asyncio.sleep(0)


async def advance_time(canvas):
    """Increments the game year every 1.5 seconds and updates the info panel.

    Args:
        canvas: The main curses window object.

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    canvas_height, canvas_width = canvas.getmaxyx()

    panel_height = game_config.PANEL_HEIGHT
    panel_width = canvas_width
    panel_start_row = canvas_height - panel_height
    panel_start_col = 0

    info_window = canvas.derwin(panel_height, panel_width, panel_start_row, panel_start_col)

    current_phrase = ""

    while True:
        if game_state.game_over:
            return

        if game_state.year in game_config.PHRASES:
            current_phrase = game_config.PHRASES[game_state.year]

        info_window.clear()
        info_window.border()

        status_text = f" Year: {game_state.year} | {current_phrase} "

        info_window.addstr(1, 2, status_text[:panel_width - 4])
        info_window.noutrefresh()

        await sleep(tics=15)
        game_state.year += 1
