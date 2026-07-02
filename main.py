import time
import curses

from curses_tools import load_frames
from animations import get_star_coroutines, fire, animate_spaceship, fill_orbit_with_garbage

TIC_TIMEOUT = 0.1
NUM_STARS = 100
STAR_SYMBOLS = "+*.:⁕◦"

SHIP_SPEED = 5
VERTICAL_SHOT_SPEED = -0.3
OBSTACLE_SPEED = 0.5


def draw(canvas):
    canvas.nodelay(True)
    curses.curs_set(0)
    canvas.clear()

    canvas_height, canvas_width = canvas.getmaxyx()
    center_row = canvas_height // 2
    center_column = canvas_width // 2

    ship_frames = load_frames(path_pattern="frames/ship/*.txt")
    obstacle_frames = load_frames(path_pattern="frames/obstacles/*.txt")

    coroutines = get_star_coroutines(
        canvas=canvas,
        canvas_height=canvas_height,
        canvas_width=canvas_width,
        star_symbols=STAR_SYMBOLS,
        num_stars=NUM_STARS
    )

    shot_coroutine = fire(
        canvas=canvas,
        start_row=center_row,
        start_column=center_column,
        rows_speed=VERTICAL_SHOT_SPEED
    )
    coroutines.append(shot_coroutine)

    ship_coroutine = animate_spaceship(
        canvas=canvas,
        start_row=center_row,
        start_column=center_column,
        frames=ship_frames,
        speed=SHIP_SPEED
    )
    coroutines.append(ship_coroutine)

    obstacle_spawner_coroutine = fill_orbit_with_garbage(
        canvas=canvas,
        frames=obstacle_frames,
        coroutines=coroutines,
        speed=OBSTACLE_SPEED,
        delay_range=(8, 20)
    )
    coroutines.append(obstacle_spawner_coroutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == "__main__":
    try:
        curses.wrapper(draw)
    except KeyboardInterrupt:
        pass
