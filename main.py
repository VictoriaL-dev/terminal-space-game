import time
import curses

from animations import get_star_coroutines, fire, animate_spaceship

TIC_TIMEOUT = 0.1
NUM_STARS = 100
STAR_SYMBOLS = "+*.:⁕◦"


def draw(canvas):
    canvas.nodelay(True)
    curses.curs_set(0)
    canvas.clear()

    canvas_height, canvas_width = canvas.getmaxyx()
    center_row = canvas_height // 2
    center_column = canvas_width // 2

    coroutines = get_star_coroutines(
        canvas=canvas,
        canvas_height=canvas_height,
        canvas_width=canvas_width,
        star_symbols=STAR_SYMBOLS,
        num_stars=NUM_STARS
    )

    shot_coroutine = fire(canvas=canvas, start_row=center_row, start_column=center_column)
    coroutines.append(shot_coroutine)

    with open("frames/ship/ship_1.txt", "r") as f: frame_1 = f.read()
    with open("frames/ship/ship_2.txt", "r") as f: frame_2 = f.read()
    ship_frames = [frame_1, frame_2]

    ship_coroutine = animate_spaceship(
        canvas=canvas,
        start_row=center_row,
        start_column=center_column,
        frames=ship_frames
    )
    coroutines.append(ship_coroutine)

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
    curses.wrapper(draw)
