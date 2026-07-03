import math


def _limit(value, min_value, max_value):
    """Limits a value within the specified minimum and maximum bounds.

    Args:
        value (float): The target value to clip.
        min_value (float): The lower bound.
        max_value (float): The upper bound.

    Returns:
        float: The clipped value restricted to the [min_value, max_value] range.
    """
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def _apply_acceleration(speed, speed_limit, forward=True):
    """Calculates non-linear speed change based on direction and limits.

    Uses a cosine wave coefficient to simulate momentum, allowing faster
    acceleration at lower speeds and slower acceleration as the speed
    approaches its maximum limit.

    Args:
        speed (float): The current speed along an axis.
        speed_limit (float): The maximum allowed speed magnitude.
        forward (bool): If True, accelerates forward (positive delta).
            If False, brakes or moves backward (negative delta). Defaults to True.

    Returns:
        float: The updated speed value, restricted by speed_limit. Returns 0
            if the absolute speed drops below 0.1.
    """
    speed_limit = abs(speed_limit)
    speed_fraction = speed / speed_limit

    delta = math.cos(speed_fraction) * 0.75

    if forward:
        result_speed = speed + delta
    else:
        result_speed = speed - delta
    result_speed = _limit(result_speed, -speed_limit, speed_limit)

    if abs(result_speed) < 0.1:
        result_speed = 0
    return result_speed


def update_speed(row_speed, column_speed, rows_direction, columns_direction,
                 row_speed_limit=2, column_speed_limit=2, fading=0.8):
    """Updates motion speed smoothly by applying friction and acceleration.

    Simulates inertia by diminishing existing speed using a fading factor and
    then applying acceleration if a control direction is engaged. This ensures
    fluid movements and natural deceleration when controls are released.

    Args:
        row_speed (float): Current vertical velocity (Y-axis).
        column_speed (float): Current horizontal velocity (X-axis).
        rows_direction (int): Vertical input direction. Expected values:
            -1 (up), 0 (none), 1 (down).
        columns_direction (int): Horizontal input direction. Expected values:
            -1 (left), 0 (none), 1 (right).
        row_speed_limit (float): Maximum absolute vertical velocity.
            Defaults to 2.
        column_speed_limit (float): Maximum absolute horizontal velocity.
            Defaults to 2.
        fading (float): Friction coefficient determining how fast the
            object slows down. Must be between 0 and 1. Defaults to 0.8.

    Raises:
        ValueError: If direction values are not within (-1, 0, 1) or fading
            is outside the [0, 1] range.

    Returns:
        (float, float): A two-element tuple containing:
            1) row_speed (float): The newly computed vertical speed.
            2) column_speed (float): The newly computed horizontal speed.
    """
    if rows_direction not in (-1, 0, 1):
        raise ValueError(f"Wrong rows_direction value {rows_direction}. Expects -1, 0 or 1.")

    if columns_direction not in (-1, 0, 1):
        raise ValueError(f"Wrong columns_direction value {columns_direction}. Expects -1, 0 or 1.")

    if fading < 0 or fading > 1:
        raise ValueError(f"Wrong columns_direction value {fading}. Expects float between 0 and 1.")

    row_speed *= fading
    column_speed *= fading

    row_speed_limit, column_speed_limit = abs(row_speed_limit), abs(column_speed_limit)

    if rows_direction != 0:
        row_speed = _apply_acceleration(row_speed, row_speed_limit, rows_direction > 0)

    if columns_direction != 0:
        column_speed = _apply_acceleration(column_speed, column_speed_limit, columns_direction > 0)

    return row_speed, column_speed
