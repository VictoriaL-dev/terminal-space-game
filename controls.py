import game_config


def read_controls(canvas):
    """Reads input keys from the terminal and detects movement actions.

    Args:
        canvas: A curses window object used to poll keyboard input via `getch()`.

    Returns:
        (int, int, bool): A three-element tuple containing:
            1) rows_direction (int): Vertical movement delta (-1 for Up, 1 for Down, 0 for None).
            2) columns_direction (int): Horizontal movement delta (-1 for Left, 1 for Right, 0 for None).
            3) space_pressed (bool): True if the spacebar was pressed, False otherwise.
    """
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == game_config.UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == game_config.DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == game_config.RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == game_config.LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == game_config.SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed
