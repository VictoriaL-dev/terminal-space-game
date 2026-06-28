import random
import curses
import asyncio
import itertools

from curses_tools import draw_frame


async def blink(canvas, row, column, symbol):
    """Animates a single star blinking at a fixed coordinate.

    The star starts with a random phase offset to desynchronize its blinking
    pattern from other stars. It then enters an infinite loop, cycling through
    four brightness states: dim, normal, bold, and normal again.

    Args:
        canvas: A curses window object where the star will be drawn.
        row (int): The vertical coordinate (Y) on the canvas.
        column (int): The horizontal coordinate (X) on the canvas.
        symbol (str): The character representing the star.

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    offset = random.randint(0, 30)
    for _ in range(offset):
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

        coroutine = blink(canvas=canvas, row=row, column=column, symbol=symbol)
        coroutines.append(coroutine)
    return coroutines


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Animates a projectile firing and flying across the screen.

    The animation begins with a two-stage muzzle flash (* then O) at the
    starting coordinates, accompanied by a system beep. The projectile then
    flies in the specified direction until it hits any boundary of the canvas,
    automatically choosing between horizontal (-) and vertical (|) symbols.

    Args:
        canvas: A curses window object where the projectile will be drawn.
        start_row (float): The initial vertical coordinate (Y).
        start_column (float): The initial horizontal coordinate (X).
        rows_speed (float, optional): Vertical speed per tick. Negative moves up,
            positive moves down. Defaults to -0.3.
        columns_speed (float, optional): Horizontal speed per tick. Negative
            moves left, positive moves right. Defaults to 0.

    Returns:
        None: The coroutine finishes and returns when the projectile moves
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


async def animate_spaceship(canvas, ship_coords, frames):
    """Animates the player's spaceship by cycling through its animation frames.

    This coroutine runs an infinite loop that sequentially displays the ship's
    ASCII art frames to create a fluid animation (e.g., flickering engine fire).
    It dynamically reads the spaceship's position from the shared game state
    dictionary and memorizes the exact coordinates where the frame was drawn
    to ensure perfect, trail-free erasing even during fast movements.

    Args:
        canvas: A curses window object where the spaceship will be drawn.
        ship_coords (dict): A mutable dictionary holding the current coordinates
            of the ship under `row` (Y) and `col` (X) keys.
        frames (list of str): A list of multiline strings representing the
            ASCII art animation frames of the spaceship.

    Returns:
        None: This coroutine runs infinitely and does not return a value.
    """
    frames_cycle = itertools.cycle(frames)

    while True:
        current_frame = next(frames_cycle)
        current_row = ship_coords["row"]
        current_col = ship_coords["col"]

        draw_frame(canvas=canvas, start_row=current_row, start_column=current_col, text=current_frame)

        for _ in range(2):
            await asyncio.sleep(0)
        draw_frame(canvas=canvas, start_row=current_row, start_column=current_col, text=current_frame, negative=True)
