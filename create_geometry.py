from paramak import Reactor, Shape, Plasma

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


plasma = Plasma(
            major_radius=620,
            minor_radius=200,
            elongation=2,
            triangularity=0.55,
            rotation_angle=10
        )

my_reactor = Reactor([water, tungsten, copper, cucrzr, plasma])

my_reactor.export_stl("reactor.stl")
my_reactor.export_dagmc_h5m("dagmc.h5m")  # , exclude=["plasma"]


os.system('mbconvert dagmc.h5m dagmc.vtk')
