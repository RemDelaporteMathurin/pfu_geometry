from typing import Tuple, Union
import math
import numpy as np


def find_center_point_of_circle(
    point_a: Tuple[float, float],
    point_b: Tuple[float, float],
    point_3: Tuple[float, float],
) -> Union[Tuple[float, float], None]:
    """
    Calculates the center of a circle passing through 3 points.
    Args:
        point_a: point 1 coordinates
        point_b: point 2 coordinates
        point_3: point 3 coordinates
    Returns:
        center of the circle coordinates or None if 3 points on a line are
        input and the radius
    """

    temp = point_b[0] * point_b[0] + point_b[1] * point_b[1]
    bc = (point_a[0] * point_a[0] + point_a[1] * point_a[1] - temp) / 2
    cd = (temp - point_3[0] * point_3[0] - point_3[1] * point_3[1]) / 2
    det = (point_a[0] - point_b[0]) * (point_b[1] - point_3[1]) - (
        point_b[0] - point_3[0]
    ) * (point_a[1] - point_b[1])

    if abs(det) < 1.0e-6:
        return None

    # Center of circle
    cx = (bc * (point_b[1] - point_3[1]) - cd * (point_a[1] - point_b[1])) / det
    cy = ((point_a[0] - point_b[0]) * cd - (point_b[0] - point_3[0]) * bc) / det

    return (cx, cy)


def distance_between_two_points(
    point_a: Tuple[float, float], point_b: Tuple[float, float]
) -> float:
    """Computes the distance between two points.
    Args:
        point_a (float, float): X, Y coordinates of the first point
        point_b (float, float): X, Y coordinates of the second point
    Returns:
        float: distance between A and B
    """

    xa, ya = point_a[0], point_a[1]
    xb, yb = point_b[0], point_b[1]
    u_vec = [xb - xa, yb - ya]
    return np.linalg.norm(u_vec)


def angle_between_two_points_on_circle(
    point_1: Tuple[float, float], point_2: Tuple[float, float], radius_of_circle: float
):

    separation = distance_between_two_points(point_1, point_2)
    isos_tri_term = (2 * math.pow(radius_of_circle, 2) - math.pow(separation, 2)) / (
        2 * math.pow(radius_of_circle, 2)
    )
    angle = math.acos(isos_tri_term)
    return angle


def find_radius_of_circle(
    center_point: Tuple[float, float],
    edge_point: Tuple[float, float],
) -> float:
    """Calculates the radius of a circle.
    Args:
        center_point: x, y coordinates of the center of te circle
        edge_point: x, y coordinates of a point on the edge of the circle
    Returns:
        the radius of the circle
    """

    if center_point == edge_point:
        return np.inf

    radius = np.sqrt(
        (center_point[0] - edge_point[0]) ** 2 + (center_point[1] - edge_point[1]) ** 2
    )

    return radius
