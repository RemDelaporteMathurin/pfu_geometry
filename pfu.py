from monoblock import Monoblock
from cadquery import exporters
import cadquery as cq

import numpy as np


class PFU:
    def __init__(
        self,
        L,
        cucrzr_inner_radius,
        cucrzr_thickness,
        target_radius,
        angle,
        thickness_mb,
        gap,
    ) -> None:

        self.L = L
        self.cucrzr_inner_radius = cucrzr_inner_radius
        self.cucrzr_thickness = cucrzr_thickness
        self.target_radius = target_radius
        self.angle = angle
        self.thickness_mb = thickness_mb
        self.gap = gap

        self.tube, self.water = self.make_tube()

        self.monoblocks = self.make_monoblocks()

        self.cut_tube_from_mbs()

    def make_monoblocks(self):
        # monoblocks on straight line
        locations = np.arange(0, self.L, step=self.thickness_mb + self.gap)

        monoblocks_straight = [
            Monoblock(
                thickness=self.thickness_mb,
                height=2.5,
                width=2.3,
                cucrzr_inner_radius=self.cucrzr_inner_radius,
                cucrzr_thickness=self.cucrzr_thickness,
                w_thickness=0.5,
                cu_thickness=0.1,
                gap=self.gap,
                location=(0, y_loc, 0),
                normal=(0, 1, 0),
                hollow=False,
            )
            for y_loc in locations
        ]
        # monoblocks on curve
        monoblocks_curve = []
        thetas = np.linspace(np.pi * 0.999, (180 - self.angle) * np.pi / 180, num=27)

        for theta in thetas:
            x_loc = self.target_radius + self.target_radius * np.cos(theta)
            y_loc = self.L + self.target_radius * np.sin(theta)

            x_normal = np.sin(theta)
            y_normal = -np.cos(theta)

            monoblocks_curve.append(
                Monoblock(
                    thickness=self.thickness_mb,
                    height=2.5,
                    width=2.3,
                    cucrzr_inner_radius=self.cucrzr_inner_radius,
                    cucrzr_thickness=self.cucrzr_thickness,
                    w_thickness=0.5,
                    cu_thickness=0.1,
                    gap=self.gap,
                    location=(x_loc, y_loc, 0),
                    normal=(x_normal, y_normal, 0),
                    xDir=(0, 0, 1),
                    hollow=False,
                )
            )
        return monoblocks_straight + monoblocks_curve

    def make_tube(self):

        water_1 = cq.Workplane("ZX").circle(self.cucrzr_inner_radius).extrude(self.L)
        water_2 = (
            cq.Workplane("ZX")
            .workplane(offset=self.L)
            .circle(self.cucrzr_inner_radius)
            .revolve(
                self.angle,
                (1, self.target_radius, 0),
                (-1, self.target_radius, 0),
            )
        )

        water = water_1.union(water_2)

        tube_1 = (
            cq.Workplane("ZX")
            .circle(self.cucrzr_inner_radius + self.cucrzr_thickness)
            .extrude(self.L)
        )
        tube_2 = (
            cq.Workplane("ZX")
            .workplane(offset=self.L)
            .circle(self.cucrzr_inner_radius + self.cucrzr_thickness)
            .revolve(
                self.angle,
                (1, self.target_radius, 0),
                (-1, self.target_radius, 0),
            )
        )
        tube_total = tube_1.union(tube_2).cut(water)

        return tube_total, water

    def cut_tube_from_mbs(self):
        """Cuts the water and CuCrZr tube from monoblocks copper to avoid overlaps"""
        for i, mb in enumerate(self.monoblocks[:-1]):
            mb.copper = mb.copper.cut(self.tube).cut(self.water)
            # exporters.export(mb.copper, "monoblocks/copper_{}.stl".format(i))


my_pfu = PFU(
    L=87.0,
    cucrzr_inner_radius=0.6,
    cucrzr_thickness=0.15,
    target_radius=25.0,
    angle=80,
    gap=0.1,
    thickness_mb=1.2,
)

if __name__ == "__main__":
    # attach everything

    print("attaching monoblocks")
    monoblocks = my_pfu.monoblocks[0].tungsten.union(my_pfu.monoblocks[0].copper)
    for mb in my_pfu.monoblocks[1:]:
        monoblocks = monoblocks.union(mb.tungsten).union(mb.copper)

    exporters.export(monoblocks, "monoblocks.stl")

    exporters.export(my_pfu.tube, "tube.stl")

    print("attaching monoblocks to tube")

    pfu = my_pfu.tube.union(monoblocks)
    exporters.export(pfu, "pfu.stl")

    # tungsten = my_pfu.monoblocks[0].tungsten
    # for mb in my_pfu.monoblocks[1:]:
    #     tungsten = tungsten.union(mb.tungsten)
    # exporters.export(tungsten, "w.stl")

    # copper = my_pfu.monoblocks[0].copper
    # for mb in my_pfu.monoblocks[1:]:
    #     copper = copper.union(mb.copper)
    # exporters.export(copper, "copper.stl")
