import asyncio

from curses_tools import draw_frame


class Obstacle:
    """Represents a physical rectangular obstacle on the 2D matrix canvas.

    Used for calculating bounding boxes for debugging displays and validating
    collisions with other game entities like shots.
    """

    def __init__(self, row, column, rows_size=1, columns_size=1, uid=None):
        """Initializes the obstacle with position spatial dimensions.

        Args:
            row (float): The current vertical coordinate (Y) of the top-left corner.
            column (float): The current horizontal coordinate (X) of the top-left corner.
            rows_size (int): Vertical thickness / height of the hit box.
            columns_size (int): Horizontal length / width of the hit box.
            uid (str): Unique identifier assigned to the obstacle instance.

        Returns:
            Obstacle: An obstacle instance.
        """
        self.row = row
        self.column = column
        self.rows_size = rows_size
        self.columns_size = columns_size
        self.uid = uid

    def get_bounding_box_frame(self):
        """Generates a text-based ASCII frame representing the bounding box border.

        Returns:
            str: A multiline string composed of lines forming a box outline.
        """
        rows, columns = self.rows_size + 1, self.columns_size + 1
        return "\n".join(_get_bounding_box_lines(rows, columns))

    def get_bounding_box_corner_pos(self):
        """Calculates the alignment coordinate for drawing the outer bounding box.

        Since the frame padding expands by 1 cell outwards, the corner shifts.

        Returns:
            (float, float): The (row, column) coordinate for drawing.
        """
        return self.row - 1, self.column - 1

    def dump_bounding_box(self):
        """Packages position coordinates and the text frame of the bounding box.

        Returns:
            (float, float, str): A tuple containing:
                1) row (float): Adjusted bounding box vertical coordinate.
                2) column (float): Adjusted bounding box horizontal coordinate.
                3) frame (str): ASCII representation of the bounding box lines.
        """
        row, column = self.get_bounding_box_corner_pos()
        return row, column, self.get_bounding_box_frame()

    def has_collision(self, obj_corner_row, obj_corner_column, obj_size_rows=1, obj_size_columns=1):
        """Determines if a target entity collides with this obstacle instance.

        Args:
            obj_corner_row (float): Top-left row index of the checked object.
            obj_corner_column (float): Top-left column index of the checked object.
            obj_size_rows (int): Total vertical span of the object. Defaults to 1.
            obj_size_columns (int): Total horizontal span. Defaults to 1.

        Returns:
            bool: True if bounding rectangles overlap at any point, False otherwise.
        """
        return has_collision(
            (self.row, self.column),
            (self.rows_size, self.columns_size),
            (obj_corner_row, obj_corner_column),
            (obj_size_rows, obj_size_columns),
        )


def _get_bounding_box_lines(rows, columns):
    """Yields text strings line-by-line to build an ASCII frame box.

    Args:
        rows (int): Expected inner vertical cell size.
        columns (int): Expected inner horizontal cell size.

    Returns:
        str: A single line string sequence forming part of the visual outline.
    """
    yield " " + "-" * columns + " "
    for _ in range(rows):
        yield "|" + " " * columns + "|"
    yield " " + "-" * columns + " "


async def show_obstacles(canvas, obstacles):
    """Infinite loop displaying visual bounding box wireframes for debugging.

    Draws borders around all currently active obstacles in the passed list,
    updates them every tick, and performs negative wipes to clear old frames.

    Args:
        canvas: A curses window object where the debug boxes are drawn.
        obstacles (list of Obstacle): Shared list tracking currently live obstacles.

    Returns:
        None: Runs indefinitely until the parent async loop closes.
    """
    while True:
        boxes = []

        for obstacle in obstacles:
            boxes.append(obstacle.dump_bounding_box())

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame, negative=True)


def _is_point_inside(corner_row, corner_column, size_rows, size_columns, point_row,
                     point_row_column):
    """Validates if a discrete point resides inside a defined rectangle.

    Args:
        corner_row (float): Top-left Y axis reference bound.
        corner_column (float): Top-left X axis reference bound.
        size_rows (int): Rectangle height threshold.
        size_columns (int): Rectangle width threshold.
        point_row (float): Target point Y coordinate.
        point_row_column (float): Target point X coordinate.

    Returns:
        bool: True if the target coordinates fall inside the boundaries, False otherwise.
    """
    rows_flag = corner_row <= point_row < corner_row + size_rows
    columns_flag = corner_column <= point_row_column < corner_column + size_columns
    return rows_flag and columns_flag


def has_collision(obstacle_corner, obstacle_size, obj_corner, obj_size=(1, 1)):
    """Verifies geometric overlaps between two separate 2D bounding boxes.

    Checks intersection points by cross-referencing corners of both entities
    to find intersections.

    Args:
        obstacle_corner (tuple of float): Top-left (row, column) of obstacle.
        obstacle_size (tuple of int): (height, width) dimensions of obstacle.
        obj_corner (tuple of float): Top-left (row, column) of moving object.
        obj_size (tuple of int): (height, width) of moving object.
            Defaults to (1, 1).

    Returns:
        bool: True if any vertex crosses into the opposing bounds, False otherwise.
    """
    opposite_obstacle_corner = (
        obstacle_corner[0] + obstacle_size[0] - 1,
        obstacle_corner[1] + obstacle_size[1] - 1,
    )

    opposite_obj_corner = (
        obj_corner[0] + obj_size[0] - 1,
        obj_corner[1] + obj_size[1] - 1,
    )

    return any([
        _is_point_inside(*obstacle_corner, *obstacle_size, *obj_corner),
        _is_point_inside(*obstacle_corner, *obstacle_size, *opposite_obj_corner),

        _is_point_inside(*obj_corner, *obj_size, *obstacle_corner),
        _is_point_inside(*obj_corner, *obj_size, *opposite_obstacle_corner),
    ])
