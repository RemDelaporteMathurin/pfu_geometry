from monoblock import Monoblock
from cadquery import exporters
import cadquery as cq

import numpy as np


class PFU:
    def __init__(
        self, L, target_radius, angle, nb_mbs_on_curve=27, **monoblocks_args
    ) -> None:

        self.L = L
        self.target_radius = target_radius
        self.angle = angle

        self.nb_mbs_on_curve = (
            nb_mbs_on_curve  # ideally this should be computed from gap
        )

        self.monoblocks_args = monoblocks_args

    def make_solid(self):
        self.tube, self.water = self.make_tube()

        self.monoblocks = self.make_monoblocks()

        self.cut_tube_from_mbs()

        self.tungsten = self.monoblocks[0].tungsten
        for mb in self.monoblocks[1:]:
            self.tungsten = self.tungsten.union(mb.tungsten)

        self.copper = self.monoblocks[0].copper
        for mb in self.monoblocks[1:]:
            self.copper = self.copper.union(mb.copper)

    def make_monoblocks(self):
        # monoblocks on straight line
        if self.L == 0:
            locations = []
        else:
            locations = np.arange(
                0,
                self.L,
                step=self.monoblocks_args["thickness"] + self.monoblocks_args["gap"],
            )

        monoblocks_straight = [
            Monoblock(
                **self.monoblocks_args,
                location=(0, y_loc, 0),
                normal=(0, 1, 0),
                hollow=False,
            )
            for y_loc in locations
        ]
        # monoblocks on curve
        monoblocks_curve = []
        thetas = np.linspace(
            np.pi * 0.999, (180 - self.angle) * np.pi / 180, num=self.nb_mbs_on_curve
        )

        for theta in thetas:
            x_loc = self.target_radius + self.target_radius * np.cos(theta)
            y_loc = self.L + self.target_radius * np.sin(theta)

            x_normal = np.sin(theta)
            y_normal = -np.cos(theta)

            monoblocks_curve.append(
                Monoblock(
                    thickness=self.monoblocks_args["thickness"],
                    height=2.5,
                    width=2.3,
                    cucrzr_inner_radius=self.monoblocks_args["cucrzr_inner_radius"],
                    cucrzr_thickness=self.monoblocks_args["cucrzr_thickness"],
                    w_thickness=0.5,
                    cu_thickness=0.1,
                    gap=self.monoblocks_args["gap"],
                    location=(x_loc, y_loc, 0),
                    normal=(x_normal, y_normal, 0),
                    xDir=(0, 0, 1),
                    hollow=False,
                )
            )
        return monoblocks_straight + monoblocks_curve

    def make_tube(self):

        water_2 = (
            cq.Workplane("ZX")
            .workplane(offset=self.L)
            .circle(self.monoblocks_args["cucrzr_inner_radius"])
            .revolve(
                self.angle,
                (1, self.target_radius, 0),
                (-1, self.target_radius, 0),
            )
        )
        if self.L != 0:
            water_1 = (
                cq.Workplane("ZX")
                .circle(self.monoblocks_args["cucrzr_inner_radius"])
                .extrude(self.L)
            )
            water = water_1.union(water_2)
        else:
            water = water_2

        tube_2 = (
            cq.Workplane("ZX")
            .workplane(offset=self.L)
            .circle(
                self.monoblocks_args["cucrzr_inner_radius"]
                + self.monoblocks_args["cucrzr_thickness"]
            )
            .revolve(
                self.angle,
                (1, self.target_radius, 0),
                (-1, self.target_radius, 0),
            )
        )

        if self.L != 0:
            tube_1 = (
                cq.Workplane("ZX")
                .circle(
                    self.monoblocks_args["cucrzr_inner_radius"]
                    + self.monoblocks_args["cucrzr_thickness"]
                )
                .extrude(self.L)
            )

            tube_total = tube_1.union(tube_2).cut(water)
        else:
            tube_total = tube_2

        return tube_total, water

    def cut_tube_from_mbs(self):
        """Cuts the water and CuCrZr tube from monoblocks copper to avoid overlaps"""
        for i, mb in enumerate(self.monoblocks[:-1]):
            mb.copper = mb.copper.cut(self.tube).cut(self.water)
            # exporters.export(mb.copper, "monoblocks/copper_{}.stl".format(i))


if __name__ == "__main__":
    my_pfu = PFU(
        L=87.0,
        target_radius=25.0,
        angle=80,
        gap=0.1,
        thickness=1.2,
        height=2.5,
        width=2.3,
        cucrzr_inner_radius=0.6,
        cucrzr_thickness=0.15,
        w_thickness=0.5,
        cu_thickness=0.1,
    )
    my_pfu.make_solid()
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
