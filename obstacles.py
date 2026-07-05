import asyncio

from curses_tools import draw_frame


class Obstacle:
    """Represents a physical rectangular obstacle on the 2D matrix canvas."""

    def __init__(self, row, column, rows_size=1, columns_size=1, uid=None):
        """Initializes the obstacle with position spatial dimensions.

        Args:
            row (int): The current vertical coordinate (Y) of the top-left corner.
            column (int): The current horizontal coordinate (X) of the top-left corner.
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
        top_bottom = f" {'-' * (self.columns_size + 1)} "
        middle_lines = [f"|{' ' * (self.columns_size + 1)}|" for _ in range(self.rows_size + 1)]
        return "\n".join([top_bottom] + middle_lines + [top_bottom])

    def get_bounding_box_corner_pos(self):
        """Calculates the alignment coordinate for drawing the outer bounding box.

        Returns:
            (int, int): The (row, column) coordinate for drawing.
        """
        return self.row - 1, self.column - 1

    def dump_bounding_box(self):
        """Packages position coordinates and the text frame of the bounding box.

        Returns:
            (int, int, str): A tuple containing:
                1) row (int): Adjusted bounding box vertical coordinate.
                2) column (int): Adjusted bounding box horizontal coordinate.
                3) frame (str): ASCII representation of the bounding box lines.
        """
        row, column = self.get_bounding_box_corner_pos()
        return row, column, self.get_bounding_box_frame()

    def has_collision(self, obj_corner_row, obj_corner_column, obj_size_rows=1, obj_size_columns=1):
        """Determines if a target entity collides with this obstacle instance.

        Args:
            obj_corner_row (int): Top-left row index of the checked object.
            obj_corner_column (int): Top-left column index of the checked object.
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


def has_collision(obstacle_corner, obstacle_size, obj_corner, obj_size=(1, 1)):
    """Verifies geometric overlaps between two separate 2D bounding boxes.

    Uses the Axis-Aligned Bounding Box (AABB) intersection algorithm.
    Guarantees absolute collision precision for rectangles of any aspect ratio.

    Args:
        obstacle_corner (tuple of int): Top-left (row, column) of obstacle.
        obstacle_size (tuple of int): (height, width) dimensions of obstacle.
        obj_corner (tuple of int): Top-left (row, column) of moving object.
        obj_size (tuple of int): (height, width) of moving object.
            Defaults to (1, 1).

    Returns:
        bool: True if any vertex crosses into the opposing bounds, False otherwise.
    """
    a_top, a_left = obstacle_corner
    a_bottom = a_top + obstacle_size[0]
    a_right = a_left + obstacle_size[1]

    b_top, b_left = obj_corner
    b_bottom = b_top + obj_size[0]
    b_right = b_left + obj_size[1]

    return not (a_right <= b_left or b_right <= a_left or a_bottom <= b_top or b_bottom <= b_top)


async def show_obstacles(canvas, obstacles):
    """Infinite loop displaying visual bounding box wireframes for debugging.

    Args:
        canvas: A curses window object where the debug boxes are drawn.
        obstacles (list of Obstacle): Shared list tracking currently live obstacles.

    Returns:
        None: Runs indefinitely until the parent async loop closes.
    """
    while True:
        boxes = []
        for obstacle in obstacles:
            row, column, frame = obstacle.dump_bounding_box()
            boxes.append((round(row), round(column), frame))

        for row, column, frame in boxes:
            draw_frame(canvas=canvas, start_row=row, start_column=column, frame=frame)

        await asyncio.sleep(0)

        for row, column, frame in boxes:
            draw_frame(canvas=canvas, start_row=row, start_column=column, frame=frame, negative=True)
