import time
import curses

import game_config
from curses_tools import load_frames
from curses_tools import get_frame_size
from animations import get_star_coroutines, animate_spaceship, fill_orbit_with_garbage


def draw(canvas):
    canvas.nodelay(True)
    curses.curs_set(0)
    canvas.clear()

    ship_frames = load_frames(path_pattern="frames/ship/*.txt")
    obstacle_frames = load_frames(path_pattern="frames/obstacles/*.txt")

    canvas_height, canvas_width = canvas.getmaxyx()
    ship_height, ship_width = get_frame_size(frame=ship_frames[0])
    center_row = (canvas_height // 2) - (ship_height // 2)
    center_column = (canvas_width // 2) - (ship_width // 2)

    game_config.coroutines = get_star_coroutines(
        canvas=canvas,
        canvas_height=canvas_height,
        canvas_width=canvas_width
    )

    ship_coroutine = animate_spaceship(
        canvas=canvas,
        start_row=center_row,
        start_column=center_column,
        frames=ship_frames
    )
    game_config.coroutines.append(ship_coroutine)

    obstacle_spawner_coroutine = fill_orbit_with_garbage(
        canvas=canvas,
        frames=obstacle_frames,
        delay_range=game_config.OBSTACLE_DELAY_RANGE
    )
    game_config.coroutines.append(obstacle_spawner_coroutine)

    while True:
        for coroutine in game_config.coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                game_config.coroutines.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(game_config.TIC_TIMEOUT)


if __name__ == "__main__":
    try:
        curses.wrapper(draw)
    except KeyboardInterrupt:
        pass
