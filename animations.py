import random
import curses
import asyncio
import itertools

from controls import read_controls
from curses_tools import draw_frame
from curses_tools import get_frame_size

SHIP_SPEED = 5


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
    for _ in range(offset_tics):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


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


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Animates a shot firing and flying across the screen.

    The animation begins with a two-stage muzzle flash (* then O) at the
    starting coordinates, accompanied by a system beep. The shot then
    flies in the specified direction until it hits any boundary of the canvas,
    automatically choosing between horizontal (-) and vertical (|) symbols.

    Args:
        canvas: A curses window object where the shot will be drawn.
        start_row (int): The initial vertical coordinate (Y) for the shot.
        start_column (int): The initial horizontal coordinate (X) for the shot.
        rows_speed (float): Vertical speed per tick. Negative moves up,
            positive moves down. Defaults to -0.3.
        columns_speed (float): Horizontal speed per tick. Negative
            moves left, positive moves right. Defaults to 0.

    Returns:
        None: The coroutine finishes and returns when the shot moves
            off-screen or hits a border.
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
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, frames):
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

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    row, column = start_row, start_column
    canvas_height, canvas_width = canvas.getmaxyx()

    ship_sizes = [get_frame_size(text=frame) for frame in frames]
    ship_height = max([size[0] for size in ship_sizes])
    ship_width = max([size[1] for size in ship_sizes])

    duplicated_frames = [frame for frame in frames for _ in range(2)]
    frames_cycle = itertools.cycle(duplicated_frames)

    for current_frame in frames_cycle:
        rows_direction, columns_direction, space_pressed = read_controls(canvas=canvas)

        if rows_direction != 0 or columns_direction != 0:
            next_row = row + (rows_direction * SHIP_SPEED)
            next_column = column + (columns_direction * SHIP_SPEED)

            row = max(0, min(next_row, canvas_height - ship_height - 1))
            column = max(1, min(next_column, canvas_width - ship_width - 1))

        draw_frame(canvas=canvas, start_row=row, start_column=column, text=current_frame)
        await asyncio.sleep(0)
        draw_frame(canvas=canvas, start_row=row, start_column=column, text=current_frame, negative=True)
