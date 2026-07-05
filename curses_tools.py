import glob


def draw_frame(canvas, start_row, start_column, frame, negative=False):
    """Draws or erases a multiline text fragment on the canvas.

    Args:
        canvas: A curses window object where the frame will be rendered.
        start_row (float or int): The vertical starting coordinate (Y) for the top
            of the frame.
        start_column (float or int): The horizontal starting coordinate (X) for the
            left side of the frame.
        frame (str): A multiline string containing the ASCII art frame to draw.
        negative (bool): If True, replaces all non-space characters
            with spaces to erase the frame from the screen. Defaults to False.

    Returns:
        None: This coroutine does not return a value.
    """
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(frame.splitlines(), int(start_row)):
        if row < 0: continue
        if row >= rows_number: break

        for column, symbol in enumerate(line, int(start_column)):
            if column < 0: continue
            if column >= columns_number: break
            if symbol == " ": continue
            if row == rows_number - 1 and column == columns_number - 1: continue

            symbol = symbol if not negative else " "
            canvas.addch(row, column, symbol)


def get_frame_size(frame):
    """Calculates the dimensions (height, width) of a multiline text fragment.

    Args:
        frame (str): A multiline string representing the ASCII art frame.

    Returns:
        (int, int): A two-element tuple containing:
            1) rows (int): The total number of rows (height) of the frame.
            2) columns (int): The maximum number of columns (width) found among all lines.
    """
    lines = frame.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def load_frames(path_pattern):
    """Loads and reads text frames from files matching a glob pattern.

    Args:
        path_pattern (str): A glob pattern string specifying the location of the frame files.

    Returns:
        list of str: A sorted list containing the textual content of each loaded frame.
    """
    frame_paths = glob.glob(path_pattern)
    frames = []
    for path in frame_paths:
        with open(path, "r", encoding="utf-8") as file:
            frames.append(file.read())
    return frames
