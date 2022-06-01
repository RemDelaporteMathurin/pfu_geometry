from pfu import PFU
from target import Target
import cadquery as cq

import numpy as np

from helpers import (
    find_center_point_of_circle,
    find_radius_of_circle,
    angle_between_two_points_on_circle,
)

dome_length = 66
dome_thickness = 10

A_coords = (-dome_length / 2, 0)
B_coords = (dome_length / 2, 0)
C_coords = (0, dome_thickness)

center_coords = find_center_point_of_circle(A_coords, B_coords, C_coords)

radius = find_radius_of_circle(center_coords, A_coords)


angle = angle_between_two_points_on_circle(A_coords, B_coords, radius)  # in radians

dome = Target(
    5,
    0.2,
    L=0,
    cucrzr_inner_radius=0.6,
    cucrzr_thickness=0.15,
    target_radius=radius,
    angle=angle * 180 / np.pi,
    gap=0.1,
    thickness_mb=1.2,
    nb_mbs_on_curve=54,
)


from paramak import Shape

tungsten = Shape(name="tungsten")
tungsten.solid = dome.tungsten
tungsten.rotation_axis = "X"
tungsten.workplane = "ZX"
tungsten.azimuth_placement_angle = 90
tungsten.solid = tungsten.rotate_solid(tungsten.solid)

tungsten.rotation_axis = "Y"
tungsten.azimuth_placement_angle = 85
tungsten.solid = tungsten.rotate_solid(tungsten.solid)

tungsten.solid = tungsten.solid.translate(cq.Vector(480, 0, -358))

cq.exporters.export(tungsten.solid, "dome_tungsten.stl")
