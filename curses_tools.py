def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draws or erases a multiline text fragment on the canvas.

    Iterates through each character of a text drawing (like a spaceship) and
    places it on the curses canvas at the specified coordinates. It automatically
    handles clipping at terminal boundaries to prevent errors and skips spaces
    to ensure transparent backgrounds.

    Args:
        canvas: A curses window object where the frame will be rendered.
        start_row (float or int): The vertical starting coordinate (Y) for the top
            of the frame.
        start_column (float or int): The horizontal starting coordinate (X) for the
            left side of the frame.
        text (str): A multiline string containing the ASCII art frame to draw.
        negative (bool): If True, replaces all non-space characters
            with spaces to erase the frame from the screen. Defaults to False.

    Returns:
        None: This coroutine does not return a value.
    """
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0: continue
        if row >= rows_number: break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0: continue
            if column >= columns_number: break
            if symbol == " ": continue
            if row == rows_number - 1 and column == columns_number - 1: continue

            symbol = symbol if not negative else " "
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculates the dimensions of a multiline text fragment.

    Splits the input string into individual lines to determine the total height
    and analyzes each line to find the maximum width. This is used to define
    the physical bounding box of ASCII art frames.

    Args:
        text (str): A multiline string representing the ASCII art frame.

    Returns:
        (int, int): A two-element tuple containing:
            1) rows (int): The total number of rows (height) of the frame.
            2) columns (int): The maximum number of columns (width) found among all lines.
    """
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns
