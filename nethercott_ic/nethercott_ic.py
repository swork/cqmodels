"""My Nethercott IC parts.

deck_turn_block: at medial end of barber car tracks
"""

import cadquery as cq
import math

def instances():
    return [
        'Fittings.deck_turn_block_basic',
        'ShroudRailSpacers.zero_degree',
        'ShroudRailSpacers.twelve_degree'
    ]

def mm(x):
    return x

def inches(x):
    return x * 25.4

class Fittings:
    def __init__(self):
        # Turn block supports rest on deck we're taking as a cylinder, calcs in
        # comments below
        self.deck_radius = 622.3

        # overall dimensions. +Y is toward gunwale, +Z is up/out from deck
        self.extent_X = 20  # from centerline
        self.extent_Y_pos = 20
        self.extent_Y_neg = 10
        self.extent_Z = 12.5

        # dimensions related to the inverted deck block
        self.block_foot_Y = 16  # so half this for Y screw hole centerline offset, and end radius
        self.block_Y_center_offset = self.block_foot_Y / 2 + 1  # 1 from foot edge
        self.screw_hole_X_offset = 10.25
        self.screw_hole_radius = 2
        self.block_X_thru_width = 10
        self.line_clearance_radius = 4.0

        self.line_and_block_hole_Y_extent_neg = 5  # positive is to edge

        self.foot_flare_smaller = 5
        self.foot_flare_larger = 7
        self.top_flare = 2

    def deck_turn_block_basic(self):
        base = cq.Workplane("XY")
        # Top plane
        top = (
            cq.Sketch()

            # .hull() blows up if circles touch or overlap, so try arc segments instead
            .arc((-self.screw_hole_X_offset, self.block_Y_center_offset + 0.01),
                 self.block_foot_Y / 2,
                 0,
                 -160,
                 forConstruction=True)
            .arc((self.screw_hole_X_offset, self.block_Y_center_offset + 0.01),
                 self.block_foot_Y / 2,
                 0,
                 -160,
                 forConstruction=True)
            .arc((0,0),
                 self.line_clearance_radius + self.top_flare,
                 -90,
                 -270)

            # .push([(- (self.screw_hole_X_offset), self.block_Y_center_offset + 0.01),
            #        (   self.screw_hole_X_offset , self.block_Y_center_offset + 0.01)])
            # .circle(self.block_foot_Y / 2)  # + self.top_flare)
            # .push([(0, 0)])
            # .circle(self.line_clearance_radius + self.top_flare)

            .faces()
            .hull()
        )

        # Extrude to solid and recess for deck-block's metal foot
        over = 0.5
        arcPoints = [
            (-(self.screw_hole_X_offset), self.block_Y_center_offset - self.block_foot_Y/2 - over),
            (-(self.screw_hole_X_offset + self.block_foot_Y / 2 + over), self.block_Y_center_offset),
            (-(self.screw_hole_X_offset), self.block_Y_center_offset + self.block_foot_Y/2 + over),
            (+(self.screw_hole_X_offset), self.block_Y_center_offset + self.block_foot_Y/2 + over),
            (+(self.screw_hole_X_offset + self.block_foot_Y / 2 + over), self.block_Y_center_offset),
            (+(self.screw_hole_X_offset), self.block_Y_center_offset - self.block_foot_Y/2 - over),
        ]
        block = (
            cq.Workplane("XY")
            .placeSketch(top)
            .extrude(self.extent_Z, taper=-12)
        )

        # Abs references are to the center of the line hole. Screw holes
        # are +Y and +/-X from there. Block cutout is +Y from there. Z is
        # the plane where this part touches the deck, before accounting for
        # the curvature of the deck (which will be cut away from this
        # underside). Negatives for these holes:
        neg_thru_holes = (
            cq.Workplane("XY")
            .rect(self.block_X_thru_width,
                  self.extent_Y_pos,
                  centered=(True, False))
            .extrude(self.extent_Z)

            .copyWorkplane(base)
            .circle(self.line_clearance_radius)
            .extrude(self.extent_Z)

            .copyWorkplane(base)
            .rect(self.screw_hole_X_offset * 2, self.block_Y_center_offset * 2,
                  centered=True, forConstruction=True)
            .vertices(">Y")
            .circle(2)  # two circles
            .extrude(self.extent_Z)

        )
        block = block - neg_thru_holes

        # break the top surface corners
        block = (
            block
            .faces("|Z")
            .fillet(1)
        )

        block = (
            block
            # cut a recess for the block's metal feet
            .copyWorkplane(base)
            .moveTo(*arcPoints[0])
            .threePointArc(arcPoints[1], arcPoints[2])
            .lineTo(*arcPoints[3])
            .threePointArc(arcPoints[4], arcPoints[5])
            .close()
            .extrude(1, combine='cut')
        )

        # Approximate the deck's more-or-less conical top surface (where the
        # block sits; it flares to planes nearer the gunwales) with a cylinder.
        # Deck is 2-1/8" higher at center than a horizontal plane intersecting
        # it 10" to either side. Right triangle acute angle is half the
        # tangent's acute angle, and the two lines perpendicular to the two
        # tangents cross at the center of the circle. Acute angle of triangle
        # is inverse-tangent(0.2125) -> 12 degrees. So acute angle of tangent
        # is 24 degrees. 90-24=66 is larger angle of right tri whose hypotenuse
        # ends at center. 10" is short side, so inverse-sine(66) * 10 gives
        # radius of deck: 24.5in, 622.3mm. Then, how deep to set block into
        # that cylinder so its edges intersect it? Similar calcs the other
        # direction. Extent_Y is 15mm either side of midpoint and it's
        # insiginificantly different from the corresponding arc length,
        # 15=(2*pi*622.3*theta)/360 so the intersected angle is 1.38 degrees.
        # So the short side of the right triangle with twice this acute angle
        # and hypoteneuse: 0.72mm.
        deck_radius = 622.3  # really, do the math here.
        inset_into_deck = 0.72  # and here

        filleted_block = (block
                          .faces(">Z[-2]")
                          .edges("|Y")
                          .fillet(1.5)

                          # Fit us to the deck with sandpaper, if even needed. This bottom-surface radius
                          # screws up support and rafting.
                          # .faces(">Z")
                          # .workplane(deck_radius - inset_into_deck +30.5, origin=(-30, 0, 0))  # where is the fudge need coming from?
                          # .cylinder(height=self.extent_X * 3, radius=deck_radius, direct=(1, 0, 0), combine="s")
                          )

        return filleted_block

class ShroudRailSpacers:
    def __init__(self):
        self.pin_radius = mm(2.5)
        self.pin_clearance = mm(0.2)
        self.wall_thickness = mm(2.0)
        self.end_bracket_inner_width = inches(0.4)
        self.middle_bracket_inner_width = inches(0.35)
        self.boat_bracket_thickness = mm(1.0)

    def any_degree(self, bracket_inner_width, break_degree):
        inner_radius = self.pin_radius + self.pin_clearance
        outer_radius = inner_radius + self.wall_thickness
        width = bracket_inner_width - self.boat_bracket_thickness
        cyl = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .circle(inner_radius)
            .extrude(width)
        )
        neg_cyl = (
            cq.Workplane(cq.Plane.XY().rotated((break_degree, 0, 0)))
            .workplane(width/2)
            .circle(outer_radius * 3)  # way big enough
            .extrude(width * 3)  # way far enough
        )
        return cyl - neg_cyl


    def zero_degree(self):
        return self.any_degree(self.middle_bracket_inner_width, 0.0)

    def twelve_degree(self):
        return self.any_degree(self.end_bracket_inner_width, 12.0)

