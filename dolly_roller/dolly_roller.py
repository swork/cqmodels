"""
CQ model of a half-roller to support the front part of IC dollies onto and
off of the road trailer.
"""

import os
import math
import cadquery as cq

def mm(mm: float) -> float:
    return mm

def inches(mm: float) -> float:
    return mm * 25.4

PARAMS = {
    'axle radius': inches(0.5),
    'bearing radial clearance': mm(0.0),
    'fixed radial clearance': mm(0.5),  # 0 was too little in PLA
    'interference radial clearance': mm(0.15),  # 0 was too little in PLA, 0.5 way too much
    'axial clearance': mm(1),
    'wall thickness': mm(2.5),
    'full width': inches(4.0),
    'full flat width': inches(3.0),  # matching the width of the road trailer central rail
    'max radius': inches(1.5),
    'flange flat': mm(3),
    'roller bearing diameter': inches(0.25),
    'spacer flange radial': mm(3),
    'flanges axial': mm(3),
    'interference overlap': mm(8),
    'cage outer clearance': mm(1),
    'cage inner clearance': mm(1),
    'cage axial clearance': mm(1),
    'cage bearing clearance': mm(0.4),
    'bearingcenterspacing': inches(0.35),
    'length overall': os.environ.get('LENGTH_OVERALL_MM', inches(12)),
    'central support gap': os.environ.get('CENTRAL_SUPPORT_GAP_MM', 0),
}

class Roller:
    def __init__(self):
        for param in PARAMS.keys():
            setattr(self, param.replace(' ', '_'), PARAMS[param])
        self._roller_cylinder_inner_radius = self.axle_radius + self.roller_bearing_diameter + self.bearing_radial_clearance
        self._roller_cylinder_outer_radius = self._roller_cylinder_inner_radius + self.wall_thickness
        self._axle_mating_cylinder_inner_radius = self.axle_radius + self.fixed_radial_clearance
        self._roller_Z = self.full_width / 2 - self.central_support_gap / 2
                       
    def roller(self):
        angled_face_Z = self._roller_Z - self.full_flat_width / 2 - self.flange_flat
        angled_face_X = self.max_radius - self._roller_cylinder_outer_radius

        solid = (cq.Workplane("XZ")
                 .line(0, self._roller_Z)  # current workplane's Y
                 .line(self._roller_cylinder_outer_radius, 0)
                 .line(0, -(self.full_flat_width / 2))
                 .line(angled_face_X, -angled_face_Z)
                 .line(0, -(self.flange_flat))
                 .close()
                 .revolve(360)
                 .faces("<Z")
                 .workplane()
                 .circle(self._roller_cylinder_inner_radius)
                 .cutThruAll())
        return solid

    def spacer(self):
        cylinder_outer_radius = self._axle_mating_cylinder_inner_radius + self.wall_thickness
        length = self.length_overall - self.full_width - self.flanges_axial * 4 - self.axial_clearance
        solid = (cq.Workplane("XY")
                 .circle(cylinder_outer_radius + self.spacer_flange_radial)
                 .extrude(self.flanges_axial)
                 .faces("<Z")
                 .circle(cylinder_outer_radius)
                 .extrude(self.length_overall / 2 - self.flanges_axial - self.axial_clearance)
                 .circle(self._axle_mating_cylinder_inner_radius)
                 .cutThruAll())
        return solid

    def cap(self):
        interference_outer_radius = self.axle_radius + self.roller_bearing_diameter + self.bearing_radial_clearance - self.interference_radial_clearance
        surface_outer_radius = self._roller_cylinder_outer_radius
        solid = (cq.Workplane("XY")
                 .circle(surface_outer_radius)
                 .extrude(self.flanges_axial)
                 .circle(interference_outer_radius)
                 .extrude(self.interference_overlap)
                 .circle(self._axle_mating_cylinder_inner_radius)
                 .cutThruAll())
        return solid

    def cage(self):
        roller_center_radius = self.axle_radius + (self.roller_bearing_diameter / 2)
        roller_center_circumference = math.pi * roller_center_radius * 2
        roller_count = int(roller_center_circumference // self.bearingcenterspacing)
        print(f'cr:{roller_center_radius} cc:{roller_center_circumference} rc:{roller_count}')
        solid = (cq.Workplane("XY")
                 .circle(self._roller_cylinder_inner_radius - self.cage_outer_clearance)
                 .extrude(self._roller_Z - self.interference_overlap * 2 - self.cage_axial_clearance)
                 .faces("<Z")
                 .workplane()
                 .polygon(roller_count, roller_center_radius * 2, forConstruction=True)
                 .vertices()
                 .hole(self.roller_bearing_diameter + self.cage_bearing_clearance)
                 .faces("<Z")
                 .workplane()
                 .circle(self._roller_cylinder_inner_radius - self.cage_outer_clearance)
                 .extrude(self.flanges_axial)
                 .faces(">Z")
                 .workplane(invert=True)
                 .circle(self._roller_cylinder_inner_radius - self.cage_outer_clearance)
                 .extrude(self.flanges_axial)
                 .faces("<Z")
                 .workplane()
                 .circle(self.axle_radius + self.cage_inner_clearance)
                 .cutThruAll()
                 )
        return solid

    def bearing(self):
        solid = (cq.Workplane("XY")
                 .circle(self.roller_bearing_diameter / 2)
                 .extrude(inches(1)))
        return solid

def instances():
    return [ 'Roller.roller', 'Roller.spacer', 'Roller.cap', 'Roller.cage', 'Roller.bearing' ]

# def instance():
#     select = os.environ.get('SELECT', 'dolly_roller')
#     r = Roller()
#     if select == 'roller':
#         return r.roller()
#     elif select == 'cap':
#         return r.cap()
#     elif select == 'cage':
#         return r.cage()
#     elif select == 'spacer':
#         return r.spacer()
#     else:
#         # agglomerate into one .stl
#         raise RuntimeError("implement agglomeration")
