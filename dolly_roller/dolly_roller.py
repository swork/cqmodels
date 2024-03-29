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
    'axle radius': os.environ.get('AXLE_DIAMETER_MM', mm(25.7)) / 2,  # nominal 25.4 but measures big
    'bearing radial clearance': mm(0.2),
    'fixed radial clearance': mm(1),  # 0 was too little in PLA, 0.5 too little for bearing slop
    'cap radial clearance': mm(2),
    'cap radial interference': mm(0.15),
    'axial clearance': mm(1),
    'wall thickness': mm(4.0),  # 2.5 roller surface was flimsy in PLA
    'full width': inches(4.0),
    'full flat width': inches(3.0),  # matching the width of the road trailer central rail
    'max radius': inches(1.5),
    'flange flat': mm(3),
    'roller bearing diameter': inches(0.25),
    'spacer flange radial': mm(3),
    'spacer wall thickness': mm(2.5),
    'flanges axial': mm(3),
    'interference overlap': mm(8),
    'hub cap interference overlap': mm(5.5),
    'cage outer clearance': mm(1.35),  # troublesome: sets click-in for rollers
    'cage inner clearance': mm(1),
    'cage thickness': mm(4.4),  # close control over click-in for rollers, but still varies with inner circle size
    'cage axial clearance': mm(1),
    'cage bearing clearance': mm(0.65),  # 0.4 was tight against 1/4" acetal rod in PETG
    'bearing center spacing': inches(0.35),
    'length overall': os.environ.get('LENGTH_OVERALL_MM', inches(12)),
    'central support gap': os.environ.get('CENTRAL_SUPPORT_GAP_MM', 0),
    'hub sleeve distal radius': mm(25.3),
    'hub sleeve medial radius': mm(23.3),
    'hub sleeve distal axial': mm(11.0),  # including a chamfer
    'hub sleeve interference': mm(0.1),
    'hub sleeve axial total': inches(4) - mm(4),
    'hub sleeve axial clearance': mm(2),
    'hub sleeve additional bearing radial clearance': mm(0.2),
    'hub sleeve inner medial radius adjustment': - mm(0.5),
    'hub sleeve inner medial adjustment distance': mm(19),
}

def axle_support():
    solid = (cq.Workplane("XY")
             .rect(inches(1.25), inches(1.25))
             .extrude(inches(0.85))
             .edges("|Z")
             .chamfer(inches(0.25))
             .circle(PARAMS['axle radius'] - inches(0.125))
             .cutThruAll()
             )
    negative = (cq.Workplane("XY")
                .circle(PARAMS['axle radius'] + PARAMS['fixed radial clearance'])
                .extrude(inches(0.4))
                )
    return solid - negative

class Roller:
    def __init__(self):
        for param in PARAMS.keys():
            setattr(self, param.replace(' ', '_'), PARAMS[param])
        self._roller_cylinder_inner_radius = self.axle_radius + self.roller_bearing_diameter + self.bearing_radial_clearance
        self._roller_cylinder_outer_radius = self._roller_cylinder_inner_radius + self.wall_thickness
        self._axle_mating_cylinder_inner_radius = self.axle_radius + self.fixed_radial_clearance
        self._roller_Z = self.full_width / 2 - self.central_support_gap / 2
        self._cage_length = self._roller_Z - self.interference_overlap * 2 - self.cage_axial_clearance
        self._sleeve_axial = (self.hub_sleeve_axial_total / 2 - self.spacer_wall_thickness) - self.hub_sleeve_axial_clearance

    def hub_outer(self):
        """Wheel hub sleeve, not part of the roller but shares parts and dimensions"""
        radii_difference = self.hub_sleeve_distal_radius - self.hub_sleeve_medial_radius
        solid = (cq.Workplane("XZ")
                 .line(0, self._sleeve_axial)
                 .line(self.hub_sleeve_medial_radius, 0)
                 .line(0, -(self._sleeve_axial - self.hub_sleeve_distal_axial))
                 .line(radii_difference, -radii_difference)
                 .line(0, -(self.hub_sleeve_distal_axial - radii_difference))
                 .close()
                 .revolve(360)
                 .faces("<Z")
                 .workplane()
                 .circle(self._roller_cylinder_inner_radius + self.hub_sleeve_additional_bearing_radial_clearance)
                 .cutThruAll()
                 )
        return solid

    def hub_inner(self):
        hub = self.hub_outer()

        sleeve_neg = (cq.Workplane("XY")
                      .workplane(-self._sleeve_axial, invert=True)
                      .circle(self.hub_sleeve_distal_radius)  # "big enough"
                      .circle(self.hub_sleeve_medial_radius + self.hub_sleeve_inner_medial_radius_adjustment)  # a neg quantity
                      .extrude(self.hub_sleeve_inner_medial_adjustment_distance)
                      .edges("<Z")
                      .chamfer(0.5)
                      )
        return hub - sleeve_neg

    def washer(self):
        """Space the two hub races."""
        # overall length minus what's used: 2xinterference_overlap (caps), 2xcage lengths, 1xcage_axial_clearance
        washer_length = (
            self.hub_sleeve_axial_total - (
                2 * self.interference_overlap
                + 2 * self._cage_length
                + self.cage_axial_clearance
            )
        ) - mm(7)  # forgot hubs are inset a bit, and somehow missed by more too.
        solid = (cq.Workplane("XY")
                 .circle(self.axle_radius + self.roller_bearing_diameter)
                 .extrude(washer_length)
                 .faces("<Z")
                 .workplane()
                 .circle(self._axle_mating_cylinder_inner_radius + mm(2))
                 .cutThruAll()
                 )
        return solid

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
        cylinder_outer_radius = self._axle_mating_cylinder_inner_radius + self.spacer_wall_thickness
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

    def hub_cap(self):
        interference_outer_radius = self.axle_radius + self.roller_bearing_diameter + self.bearing_radial_clearance + self.cap_radial_interference
        surface_outer_radius = self._roller_cylinder_outer_radius
        solid = (cq.Workplane("XY")
                 .circle(surface_outer_radius)
                 .extrude(self.flanges_axial)
                 .circle(interference_outer_radius)
                 .extrude(self.hub_cap_interference_overlap)
                 .circle(self.axle_radius + self.cap_radial_clearance)
                 .cutThruAll())
        return solid

    def roller_cap(self):
        interference_outer_radius = self.axle_radius + self.roller_bearing_diameter + self.bearing_radial_clearance + self.cap_radial_interference
        surface_outer_radius = self._roller_cylinder_outer_radius
        solid = (cq.Workplane("XY")
                 .circle(surface_outer_radius)
                 .extrude(self.flanges_axial)
                 .circle(interference_outer_radius)
                 .extrude(self.interference_overlap)
                 .circle(self.axle_radius + self.cap_radial_clearance)
                 .cutThruAll())
        return solid

    def cage(self):
        roller_center_radius = self.axle_radius + (self.roller_bearing_diameter / 2)
        roller_center_circumference = math.pi * roller_center_radius * 2
        roller_count = int(roller_center_circumference // self.bearing_center_spacing)
        cage_outer_radius = self.axle_radius + self.cage_inner_clearance + self.cage_thickness
        print(f'cr:{roller_center_radius} cc:{roller_center_circumference} rc:{roller_count}')
        solid = (cq.Workplane("XY")
                 .circle(cage_outer_radius)
                 .extrude(self._cage_length)
                 .faces("<Z")
                 .workplane()
                 .polygon(roller_count, roller_center_radius * 2, forConstruction=True)
                 .vertices()
                 .hole(self.roller_bearing_diameter + self.cage_bearing_clearance)
                 .faces("<Z")
                 .workplane()
                 .circle(cage_outer_radius)
                 .extrude(self.flanges_axial)
                 .faces(">Z")
                 .workplane(invert=True)
                 .circle(cage_outer_radius)
                 .extrude(self.flanges_axial)
                 .faces("<Z")
                 .workplane()
                 .circle(self.axle_radius + self.cage_inner_clearance)
                 .cutThruAll()
                 )
        return solid

def instances():
    return [
        'Roller.roller',
        'Roller.spacer',
        'Roller.hub_cap',
        'Roller.roller_cap',
        'Roller.cage',
        'Roller.hub_outer',
        'Roller.hub_inner',
        'Roller.washer',
        'axle_support'
    ]
