import random
import curses
import asyncio
import itertools

from obstacles import Obstacle
from physics import update_speed
from controls import read_controls
from curses_tools import draw_frame
from curses_tools import get_frame_size


async def sleep(tics=1):
    """Pauses the coroutine execution for a specified number of game ticks.

    Args:
        tics (int): The number of game ticks to wait. Defaults to 1.
    """
    for _ in range(int(tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol, offset_tics):
    """Animates a single star blinking at a fixed coordinate.

    The star starts with a random phase offset to desynchronize its blinking
    pattern from other stars. It then enters an infinite loop, cycling through
    four brightness states: dim, normal, bold, and normal again.

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


def get_star_coroutines(canvas, canvas_height, canvas_width, star_symbols, num_stars):
    """Generates a list of coroutines representing randomly distributed stars.

    This function instantiates multiple `blink` coroutines, each assigned to a
    randomly selected valid coordinate within the game field boundaries (leaving
    room for the canvas border) and initialized with a random star symbol.

    Args:
        canvas: A curses window object where the stars will be drawn.
        canvas_height (int): The maximum vertical dimension (height) of the canvas.
        canvas_width (int): The maximum horizontal dimension (width) of the canvas.
        star_symbols (str or list): A collection of characters used to visually
            represent the stars.
        num_stars (int): The total number of star coroutines to generate.

    Returns:
        list: A list of initialized coroutine objects ready to be driven by
            the main game loop via `.send(None)`.
    """
    coroutines = []

    for _ in range(num_stars):
        row = random.randint(1, canvas_height - 2)
        column = random.randint(1, canvas_width - 2)
        symbol = random.choice(star_symbols)
        offset = random.randint(0, 30)

        coroutine = blink(canvas=canvas, row=row, column=column, symbol=symbol, offset_tics=offset)
        coroutines.append(coroutine)
    return coroutines


async def fire(canvas, start_row, start_column, rows_speed, obstacles,
               obstacles_in_last_collisions, columns_speed=0):
    """Animates a shot firing, flying across the screen, and hitting obstacles.

    The animation begins with a two-stage muzzle flash (* then O) at the
    starting coordinates, accompanied by a system beep. The shot then
    flies in the specified direction until it hits any boundary of the canvas
    or collides with an obstacle tracked in the global obstacles list.

    Args:
        canvas: A curses window object where the shot will be drawn.
        start_row (int): The initial vertical coordinate (Y) for the shot.
        start_column (int): The initial horizontal coordinate (X) for the shot.
        rows_speed (float): Vertical speed per tick. Negative moves up,
            positive moves down.
        obstacles (list of Obstacle): Global list tracking active target obstacles.
        obstacles_in_last_collisions (list of Obstacle): Global list tracking obstacle collisions.
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

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(round(row), round(column), obj_size_rows=1, obj_size_columns=1):
                obstacles_in_last_collisions.append(obstacle)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, frames, ship_speed,
                            coroutines, shot_speed, obstacles, obstacles_in_last_collisions):
    """Animates the player's spaceship and manages its controls and movement.

    This coroutine calculates its own dimensions, listens for keyboard
    inputs via `read_controls` on every single tick, and updates its
    position within the screen boundaries. It runs by iterating over an
    infinite sequence of frames.

    Args:
        canvas: A curses window object where the spaceship will be drawn.
        start_row (int): The initial vertical coordinate (Y) for the spaceship.
        start_column (int): The initial horizontal coordinate (X) for the spaceship.
        frames (list of str): A list of multiline strings representing the
            ASCII art animation frames of the spaceship.
        ship_speed (float): The movement step size per game tick.
        coroutines (list): The global list of active game coroutines.
        shot_speed (float): The shot speed per game tick.
        obstacles (list of Obstacle): Global list tracking active target obstacles.
        obstacles_in_last_collisions (list of Obstacle): Global list tracking obstacle collisions.

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    row, column = start_row, start_column
    canvas_height, canvas_width = canvas.getmaxyx()

    ship_sizes = [get_frame_size(frame=frame) for frame in frames]
    ship_height = max([size[0] for size in ship_sizes])
    ship_width = max([size[1] for size in ship_sizes])

    duplicated_frames = [frame for frame in frames for _ in range(2)]
    frames_cycle = itertools.cycle(duplicated_frames)

    row_speed, column_speed = 0.0, 0.0

    for current_frame in frames_cycle:
        rows_direction, columns_direction, space_pressed = read_controls(canvas=canvas)

        if space_pressed:
            shot_row = row
            shot_column = column + (ship_width // 2)

            shot_coroutine = fire(
                canvas=canvas,
                start_row=shot_row,
                start_column=shot_column,
                rows_speed=shot_speed,
                obstacles=obstacles,
                obstacles_in_last_collisions=obstacles_in_last_collisions
            )
            coroutines.append(shot_coroutine)

        row_speed, column_speed = update_speed(
            row_speed=row_speed,
            column_speed=column_speed,
            rows_direction=rows_direction,
            columns_direction=columns_direction,
            row_speed_limit=ship_speed,
            column_speed_limit=ship_speed,
            fading=0.8
        )

        next_row = row + row_speed
        next_column = column + column_speed

        row = max(0, min(next_row, canvas_height - ship_height - 1))
        column = max(1, min(next_column, canvas_width - ship_width - 1))

        if row in (0, canvas_height - ship_height - 1): row_speed = 0.0
        if column in (1, canvas_width - ship_width - 1): column_speed = 0.0

        draw_frame(canvas=canvas, start_row=row, start_column=column, frame=current_frame)
        await asyncio.sleep(0)
        draw_frame(canvas=canvas, start_row=row, start_column=column, frame=current_frame, negative=True)


async def fly_garbage(canvas, column, frame, speed, obstacles,
                      obstacles_in_last_collisions):
    """Animates a single piece of garbage falling from the top to the bottom.

    The function draws a garbage frame, pauses for one game tick, and then
    erases it before updating its vertical position. The horizontal position
    remains constant throughout the lifetime of the garbage animation.

    Args:
        canvas: A curses window object where the garbage will be rendered.
        column (int): The fixed horizontal coordinate (X) where the garbage falls.
        frame (str): A multiline string containing the ASCII art for the garbage.
        speed (float): The vertical distance (rows) the garbage travels per tick.
        obstacles (list of Obstacle): Global list tracking active target obstacles.
        obstacles_in_last_collisions (list of Obstacle): Global list tracking obstacle collisions.

    Returns:
        None: This coroutine terminates when the garbage goes off-screen.
    """
    rows_number, columns_number = canvas.getmaxyx()
    obstacle_height, obstacle_width = get_frame_size(frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0

    obstacle = Obstacle(row, column, obstacle_height, obstacle_width)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                return

            draw_frame(canvas=canvas, start_row=row, start_column=column, frame=frame)
            await asyncio.sleep(0)
            draw_frame(canvas=canvas, start_row=row, start_column=column, frame=frame, negative=True)

            row += speed
            obstacle.row = row
            obstacle.column = column
    finally:
        if obstacle in obstacles:
            obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas, frames, coroutines, speed, delay_range,
                                  obstacles, obstacles_in_last_collisions):
    """Continuously spawns garbage at the top of the canvas at random intervals.

    This background loop measures the screen boundaries, selects a random horizontal
    coordinate, chooses a random frame from the available list, and appends a new
    garbage animation coroutine directly into the main coroutine list.

    Args:
        canvas: A curses window object where garbage tasks are deployed.
        frames (list of str): A list containing various ASCII art frames
            used to represent different garbage items.
        coroutines (list): The global list of active game coroutines.
        speed (float): The vertical falling velocity of spawned garbage items.
        delay_range (tuple of int): A tuple (min, max) representing the
            range of game ticks to wait before spawning the next item.
        obstacles (list of Obstacle): Global list tracking active target obstacles.
        obstacles_in_last_collisions (list of Obstacle): Global list tracking obstacle collisions.

    Returns:
        None: This coroutine runs infinitely.
    """
    while True:
        rows_number, columns_number = canvas.getmaxyx()

        random_frame = random.choice(frames)
        obstacle_height, obstacle_width = get_frame_size(frame=random_frame)

        max_column = columns_number - obstacle_width - 1
        random_column = random.randint(1, max(1, max_column))

        garbage_coroutine = fly_garbage(
            canvas=canvas,
            column=random_column,
            frame=random_frame,
            speed=speed,
            obstacles=obstacles,
            obstacles_in_last_collisions=obstacles_in_last_collisions
        )
        coroutines.append(garbage_coroutine)

        delay = random.randint(*delay_range)
        await sleep(tics=delay)
