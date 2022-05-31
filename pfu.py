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

        self.tube, self.water = self.make_tube()

        locations = np.arange(0, self.L, step=thickness_mb + gap)

        self.monoblocks = [
            Monoblock(
                thickness=thickness_mb,
                height=2.5,
                width=2.3,
                cucrzr_inner_radius=cucrzr_inner_radius,
                cucrzr_thickness=cucrzr_thickness,
                w_thickness=.5,
                cu_thickness=.1,
                gap=gap,
                location=(0, y_loc, 0),
                normal=(0, 1, 0),
            )
            for y_loc in locations
        ]

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

        # exporters.export(tube1, "sub_tube1.stl")
        # exporters.export(tube2, "sub_tube2.stl")

        return tube_total, water


my_pfu = PFU(
    L=87.0,
    cucrzr_inner_radius=.6,
    cucrzr_thickness=.15,
    target_radius=25.0,
    angle=80,
    gap=.1,
    thickness_mb=1.2,
)

if __name__ == "__main__":
    # attach everything
    pfu = my_pfu.tube

    for mb in my_pfu.monoblocks:
        pfu = pfu.union(mb.tungsten).union(mb.copper)

    exporters.export(pfu, "pfu.stl")

    # exporters.export(my_pfu.tube, "tube.stl")
    # exporters.export(my_mb.tungsten, "w.stl")
    # exporters.export(my_mb.copper, "copper.stl")
