from paramak import Reactor, Shape, Plasma, ITERtypeDivertor

from pfu import my_pfu

import os

water = Shape(name="water")
water.solid = my_pfu.water


tungsten = Shape(name="tungsten")
tungsten.solid = my_pfu.monoblocks[0].tungsten
for mb in my_pfu.monoblocks[1:]:
    tungsten.solid = tungsten.solid.union(mb.tungsten)

copper = Shape(name="copper")
copper.solid = my_pfu.monoblocks[0].copper
for mb in my_pfu.monoblocks[1:]:
    tungsten.solid = tungsten.solid.union(mb.copper)

cucrzr = Shape(name="cucrzr")
cucrzr.solid = my_pfu.tube


# rotate pfu around X axis
water.rotation_axis = "X"
water.workplane = "ZX"
water.azimuth_placement_angle = 90
water.solid = water.rotate_solid(water.solid)

tungsten.rotation_axis = "X"
tungsten.workplane = "ZX"
tungsten.azimuth_placement_angle = 90
tungsten.solid = water.rotate_solid(tungsten.solid)

copper.rotation_axis = "X"
copper.workplane = "ZX"
copper.azimuth_placement_angle = 90
copper.solid = water.rotate_solid(copper.solid)

cucrzr.rotation_axis = "X"
cucrzr.workplane = "ZX"
cucrzr.azimuth_placement_angle = 90
cucrzr.solid = water.rotate_solid(cucrzr.solid)

# translate pfu
import cadquery as cq

water.solid = water.solid.translate(cq.Vector(561, 0, -367 - my_pfu.L))
tungsten.solid = tungsten.solid.translate(cq.Vector(561, 0, -367 - my_pfu.L))
copper.solid = copper.solid.translate(cq.Vector(561, 0, -367 - my_pfu.L))
cucrzr.solid = cucrzr.solid.translate(cq.Vector(561, 0, -367 - my_pfu.L))


plasma = Plasma(
    major_radius=6.2e2,
    minor_radius=2e2,
    elongation=1.7,
    triangularity=0.33,
    vertical_displacement=5.7e1,
    configuration="single-null",
    rotation_angle=10,
)

divertor_model = ITERtypeDivertor(rotation_angle=10)

my_reactor = Reactor([water, tungsten, copper, cucrzr, plasma, divertor_model])

my_reactor.export_stl("reactor.stl")
# my_reactor.export_dagmc_h5m("dagmc.h5m", exclude=["plasma"])


# os.system('mbconvert dagmc.h5m dagmc.vtk')
