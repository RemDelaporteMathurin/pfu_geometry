from paramak import Reactor, Shape

from pfu import my_pfu


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

my_reactor = Reactor([water, tungsten, copper, cucrzr])


my_reactor.export_dagmc_h5m("dagmc.h5m", exclude=["plasma"])
