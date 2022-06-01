import cadquery as cq
from pfu import PFU


class Target:
    def __init__(self, nb_pfus, toroidal_gap, **kwargs) -> None:
        self.nb_pfus = nb_pfus
        self.toroidal_gap = toroidal_gap
        self.pfu_args = kwargs

        self.pfus = self.make_pfus()

        print("grouping tungsten")
        self.tungsten = self.pfus[0].tungsten
        for pfu in self.pfus[1:]:
            self.tungsten = self.tungsten.union(pfu.tungsten)

        print("grouping copper")
        self.copper = self.pfus[0].copper
        for pfu in self.pfus[1:]:
            self.copper = self.copper.union(pfu.copper)

        print("grouping tube")
        self.tube = self.pfus[0].tube
        for pfu in self.pfus[1:]:
            self.tube = self.tube.union(pfu.tube)

        print("grouping water")
        self.water = self.pfus[0].water
        for pfu in self.pfus[1:]:
            self.water = self.water.union(pfu.water)

        print("done")

    def make_pfus(self):
        mb_width = self.pfu_args["width"]
        pfu_base = PFU(**self.pfu_args)
        pfu_base.make_solid()
        pfus = []
        for i in range(self.nb_pfus):
            print("PFU {}".format(i + 1))
            # loc = mb_width / 2 + i * (mb_width + self.toroidal_gap)
            new_pfu = PFU(**self.pfu_args)
            new_pfu.tungsten = pfu_base.tungsten.translate(
                cq.Vector(0, 0, -i * (mb_width + self.toroidal_gap))
            )
            new_pfu.copper = pfu_base.copper.translate(
                cq.Vector(0, 0, -i * (mb_width + self.toroidal_gap))
            )
            new_pfu.tube = pfu_base.tube.translate(
                cq.Vector(0, 0, -i * (mb_width + self.toroidal_gap))
            )
            new_pfu.water = pfu_base.water.translate(
                cq.Vector(0, 0, -i * (mb_width + self.toroidal_gap))
            )
            pfus.append(new_pfu)
        return pfus


if __name__ == "__main__":
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

    cq.exporters.export(my_target.tungsten, "target_tungsten.stl")
    cq.exporters.export(my_target.water, "target_water.stl")
    cq.exporters.export(my_target.copper, "target_copper.stl")
    cq.exporters.export(my_target.tube, "target_tube.stl")
