from paramak import (
    Reactor,
    Shape,
    Plasma,
    ITERtypeDivertor,
    find_center_point_of_circle,
    find_radius_of_circle,
    angle_between_two_points_on_circle,
)
import numpy as np
from target import Target
import cadquery as cq
import os


def make_dome():
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

    dome_tungsten = Shape()
    dome_tungsten.solid = dome.tungsten
    dome_tungsten.rotation_axis = "X"
    dome_tungsten.workplane = "ZX"
    dome_tungsten.azimuth_placement_angle = 90
    dome_tungsten.solid = dome_tungsten.rotate_solid(dome_tungsten.solid)

    dome_tungsten.rotation_axis = "Y"
    dome_tungsten.azimuth_placement_angle = 85
    dome_tungsten.solid = dome_tungsten.rotate_solid(dome_tungsten.solid)
    dome_tungsten.solid = dome_tungsten.solid.translate(cq.Vector(480, 0, -358))

    dome_copper = Shape()
    dome_copper.solid = dome.copper
    dome_copper.rotation_axis = "X"
    dome_copper.workplane = "ZX"
    dome_copper.azimuth_placement_angle = 90
    dome_copper.solid = dome_copper.rotate_solid(dome_copper.solid)

    dome_copper.rotation_axis = "Y"
    dome_copper.azimuth_placement_angle = 85
    dome_copper.solid = dome_copper.rotate_solid(dome_copper.solid)
    dome_copper.solid = dome_copper.solid.translate(cq.Vector(480, 0, -358))

    dome_cucrzr = Shape()
    dome_cucrzr.solid = dome.tube
    dome_cucrzr.rotation_axis = "X"
    dome_cucrzr.workplane = "ZX"
    dome_cucrzr.azimuth_placement_angle = 90
    dome_cucrzr.solid = dome_cucrzr.rotate_solid(dome_cucrzr.solid)

    dome_cucrzr.rotation_axis = "Y"
    dome_cucrzr.azimuth_placement_angle = 85
    dome_cucrzr.solid = dome_cucrzr.rotate_solid(dome_cucrzr.solid)
    dome_cucrzr.solid = dome_cucrzr.solid.translate(cq.Vector(480, 0, -358))

    dome_water = Shape()
    dome_water.solid = dome.water
    dome_water.rotation_axis = "X"
    dome_water.workplane = "ZX"
    dome_water.azimuth_placement_angle = 90
    dome_water.solid = dome_water.rotate_solid(dome_water.solid)

    dome_water.rotation_axis = "Y"
    dome_water.azimuth_placement_angle = 85
    dome_water.solid = dome_water.rotate_solid(dome_water.solid)
    dome_water.solid = dome_water.solid.translate(cq.Vector(480, 0, -358))

    return dome_tungsten.solid, dome_copper.solid, dome_cucrzr.solid, dome_water.solid


def make_outer_target():
    my_target = Target(
        nb_pfus=5,
        toroidal_gap=0.2,
        L=87.0,
        cucrzr_inner_radius=0.6,
        cucrzr_thickness=0.15,
        target_radius=25.0,
        angle=80,
        gap=0.1,
        thickness_mb=1.2,
    )
    water = Shape(name="water")
    water.solid = my_target.water

    tungsten = Shape(name="tungsten")
    tungsten.solid = my_target.tungsten

    copper = Shape(name="copper")
    copper.solid = my_target.copper

    cucrzr = Shape(name="cucrzr")
    cucrzr.solid = my_target.tube

    # rotate pfu around X axis
    water.rotation_axis = "X"
    water.workplane = "ZX"
    water.azimuth_placement_angle = 90
    water.solid = water.rotate_solid(water.solid)

    tungsten.rotation_axis = "X"
    tungsten.workplane = "ZX"
    tungsten.azimuth_placement_angle = 90
    tungsten.solid = tungsten.rotate_solid(tungsten.solid)

    copper.rotation_axis = "X"
    copper.workplane = "ZX"
    copper.azimuth_placement_angle = 90
    copper.solid = copper.rotate_solid(copper.solid)

    cucrzr.rotation_axis = "X"
    cucrzr.workplane = "ZX"
    cucrzr.azimuth_placement_angle = 90
    cucrzr.solid = cucrzr.rotate_solid(cucrzr.solid)

    # translate pfu
    import cadquery as cq

    water.solid = water.solid.translate(
        cq.Vector(561, 0, -367 - my_target.pfu_args["L"])
    )
    tungsten.solid = tungsten.solid.translate(
        cq.Vector(561, 0, -367 - my_target.pfu_args["L"])
    )
    copper.solid = copper.solid.translate(
        cq.Vector(561, 0, -367 - my_target.pfu_args["L"])
    )
    cucrzr.solid = cucrzr.solid.translate(
        cq.Vector(561, 0, -367 - my_target.pfu_args["L"])
    )

    return tungsten.solid, copper.solid, cucrzr.solid, water.solid


tungsten_outer, copper_outer, cucrzr_outer, water_outer = make_outer_target()
tungsten_dome, copper_dome, cucrzr_dome, water_dome = make_dome()

tungsten = Shape(name="tungsten")
copper = Shape(name="copper")
cucrzr = Shape(name="cucrzr")
water = Shape(name="water")

tungsten.solid = tungsten_outer.union(tungsten_dome)
copper.solid = copper_outer.union(copper_dome)
cucrzr.solid = cucrzr_outer.union(cucrzr_dome)
water.solid = water_outer.union(water_dome)

plasma = Plasma(
    major_radius=6.2e2,
    minor_radius=2e2,
    elongation=1.7,
    triangularity=0.33,
    vertical_displacement=5.7e1,
    configuration="single-null",
    rotation_angle=3,
)

divertor_model = ITERtypeDivertor(rotation_angle=3)

my_reactor = Reactor([tungsten, copper, cucrzr, water, plasma, divertor_model])

my_reactor.export_stl("reactor.stl")
# my_reactor.export_dagmc_h5m("dagmc.h5m", exclude=["plasma"])


# os.system('mbconvert dagmc.h5m dagmc.vtk')
