import cadquery as cq
import OCP

import os

# construction


class Monoblock:
    def __init__(
        self,
        thickness,
        height,
        width,
        cucrzr_inner_radius,
        cucrzr_thickness,
        cu_thickness,
        w_thickness,
        gap,
        location=(0, 0, 0),
        normal=(0, 0, 1),
    ) -> None:
        """_summary_
        Args:
            thickness (float): thickness of the monoblock (mm)
            height (float): height of the monoblock in the Y direction (mm)
            width (float): width of the monoblock in the X direction (mm)
            cucrzr_inner_radius (float): inner radius of the CuCrZr pipe (mm)
            cucrzr_thickness (float): thickness of the CuCrZr pipe (mm)
            cu_thickness (float): thickness of the Cu interlayer (mm)
            w_thickness (float): thickness of W above the Cu
                (in the middle of the MB) (mm)
            gap (float): Poloidal gap between two monoblocks (mm)
        """
        self.thickness = thickness
        self.height = height
        self.width = width
        self.cucrzr_inner_radius = cucrzr_inner_radius
        self.cucrzr_thickness = cucrzr_thickness
        self.cu_thickness = cu_thickness
        self.w_thickness = w_thickness
        self.gap = gap
        self.location = location
        self.normal = normal

        self.plane = cq.Plane(self.location, normal=self.normal)
        self.make_solid()

    def make_solid(self):

        inner_cylinder = cq.Workplane(self.plane).cylinder(
            self.thickness * 2,
            self.cucrzr_inner_radius,
        )

        cucrzr = (
            cq.Workplane(self.plane)
            .cylinder(
                self.thickness + self.gap,
                self.cucrzr_inner_radius + self.cucrzr_thickness,
            )
            .cut(inner_cylinder)
        )

        copper = (
            cq.Workplane(self.plane)
            .cylinder(
                self.thickness,
                self.cucrzr_inner_radius + self.cucrzr_thickness + self.cu_thickness,
            )
            .cut(cucrzr)
            .cut(inner_cylinder)
        )

        translation_factor = (
            -self.height / 2
            + self.cucrzr_inner_radius
            + self.cucrzr_thickness
            + self.cu_thickness
            + self.w_thickness
        )
        translation = cq.Vector(-translation_factor, 0, 0)

        tungsten = (
            cq.Workplane(self.plane)
            .box(self.width, self.height, self.thickness)
            .translate(translation)
            .cut(copper)
            .cut(cucrzr)
            .cut(inner_cylinder)
        )
        self.tungsten = tungsten
        self.copper = copper
