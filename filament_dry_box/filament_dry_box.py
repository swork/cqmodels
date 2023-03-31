import cadquery as cq
from cqmodel.util import init_params

PI = 3.14159265358979323  # 'cause we like precision

def instances():
    return [
        'FilamentDryBox.spine',
        'FilamentDryBox.roller',
    ]

class FilamentDryBox:
    """Parts to support using Amazon B087FBCNKN, Vtopmart Cereal Storage Container
    as a 3d-printer filament storage/dispenser. PLA for the roller assembly parts,
    TPU for the tube grommet (TBD)
    """

    def __init__(self, params={}):
        self.params = {
            'roller center spacing': 85,
            'roller center height': 20,
            'roller overall width': 74,
            'roller bearing center plane spacing': 65,
            'ideal cone to step': 5,  # arm flat inside bearing, just for looks
            'roller to spine clearance': 3,
            'roller thickness at bearing': 2,
            'roller thickness': 3,
            'roller bush height': 1,
            'roller bush clearance': 0.7,
            'roller bush surface width': 3,
            'bearing od': 22,
            'bearing id': 8,
            'bearing width': 7,
            'bearing fillet r': 1,  # a bearing measurement
            'bearing inner race face width': 1.8,
            'bearing clearance outer': 0.2,     # extra space where nibs aren't
            'bearing interference outer': 0.2,  # nibs inward against bearing surface
            'bearing nibs count outer': 8,
            'bearing clearance inner': 0.1,
            'bearing interference inner': 0.2,  # support makes these dims inaccurate
            'bearing nibs count inner': 6,
            'spine width': 10,
            'leg fillet r': 8,
            'leg thickness': 3,
            'box taper': 4,  # diff in box width at bottom v. roller-height
        }
        init_params(self, updates=params)

        self.roller_od = (
            self.bearing_od
            + self.roller_thickness_at_bearing * 2
        )
        self.roller_outer_r = (
            self.roller_od / 2
        )
        self.roller_inner_r = (
            self.roller_outer_r - self.roller_thickness
        )
        self.roller_bush_r = (
            self.roller_inner_r - self.roller_bush_height
        )
        self.roller_bearing_mate_r = (
            self.bearing_od / 2 + self.bearing_clearance_outer
        )
        self.bearing_step_Y = (self.roller_bearing_center_plane_spacing / 2
                               - self.bearing_width / 2)
        self.arm_bearing_r = (self.bearing_id / 2
                              - self.bearing_clearance_inner)  # DRY violation
        self.arm_step_r = self.arm_bearing_r + self.bearing_inner_race_face_width
        self.arm_fillet_r = min(self.bearing_fillet_r,
                                self.arm_step_r - self.arm_bearing_r) - 0.01


    def _draw_roller_profile(self, wp):
        """Roller profile, to be revolved around Y=0.

        Y positions are relative to center of spine.

                                +-+            roller_outermost
        s.roller_bearing_mate_r | |
                                | |
                               ++ |            self.bearing_step_Y
                               |  |
                               |  |                
                               |  |
           self.roller_inner_r |  | self.roller_outer_r
                               |  |
                               |  |
                               |  |
            s.roller_bush_r +--+  |            roller_bush_surface_distal
                            +-----+
        """
        roller_inner_Y = self.spine_width / 2 + self.roller_to_spine_clearance
        roller_outer_Y = self.roller_overall_width / 2
        roller_bush_surface_distal_Y = roller_inner_Y + self.roller_bush_surface_width
        # Clockwise from bottom right of diagram
        profile = (
            wp
            .moveTo(self.roller_bush_r,            # 9, 8
                    roller_inner_Y)
            .lineTo(self.roller_bush_r,
                    roller_bush_surface_distal_Y)  # up to 9, 11
            .lineTo(self.roller_inner_r,
                    roller_bush_surface_distal_Y)  # out
            .lineTo(self.roller_inner_r,
                    self.bearing_step_Y)             # up
            .lineTo(self.roller_bearing_mate_r,
                    self.bearing_step_Y)             # out
            .lineTo(self.roller_bearing_mate_r,
                    roller_outer_Y)               # up
            .lineTo(self.roller_outer_r,
                    roller_outer_Y)               # out
            .lineTo(self.roller_outer_r,
                    roller_inner_Y)                # down to 13, 8
            .close()                               # back to 9, 8
        )
        return profile

    def roller(self):
        """Cylindrical rollers, one 8x22x7mm skateboard bearing under the
        reel rim with the inboard end a cantelevered bushing. Four required.
        """
        # Soften corners within constraints
        fillet_r = min(self.bearing_fillet_r,
                       self.roller_bush_height / 2,
                       self.roller_bush_surface_width / 2,
                       abs(self.roller_bearing_mate_r)
                       ) - 0.01

        maybe_bumpy_roller = (
            self._draw_roller_profile(cq.Workplane("XZ")
                                      .workplane(0,
                                                 (self.roller_center_spacing / 2,
                                                  self.roller_center_height)))
            .revolve(360, (0, 0), (0, 1))
            .edges()
            .fillet(fillet_r)
        )

        nibs = (
            cq.Workplane("XY", (0, 0, - self.bearing_step_Y))
            .workplane(invert=True)
            .polygon(
                self.bearing_nibs_count_outer,
                self.roller_bearing_mate_r * 2,  # diameter, sheesh
                forConstruction=True
            )
            .vertices()
            .circle(self.bearing_interference_outer)
            .extrude(self.bearing_width)
            .edges()
            .fillet(self.bearing_interference_outer - 0.01)
        )

        return maybe_bumpy_roller + nibs

    def _draw_arm_profile(self, wp):
        """Arm profile sketch, to be revolved around Y=0.

        Four of these are merged with the central spine.

        Y=0 corresponds to the center plane of the spine.

         +-\  by fillet
         | |
         | |  bearing_r
         | ++             self.bearing_step_Y
         |  |   step_r
         |  |
         |  \             cone_distal
         |   \                      arm_length
         |    \
         |     |          cone_medial
         |     |  arm_bush_r
         |     |
         +-----+

        """
        # Stick out extra so interference nibs can touch entire inner bearing race
        arm_length = self.bearing_step_Y + self.bearing_width + self.arm_fillet_r
        cone_medial = ((self.spine_width - 2)
                       + self.roller_to_spine_clearance * 2  # each side of surface
                       + self.roller_bush_surface_width)
        cone_distal = self.bearing_step_Y - self.ideal_cone_to_step
        if cone_distal < cone_medial:  # for looks, so constrain away if needed
            cone_distal = cone_medial
        arm_bush_r = self.roller_bush_r - self.roller_bush_clearance
        print(f'step_position:{self.bearing_step_Y}')
        print(f'arm_length:{arm_length}')
        print(f'bearing_r:{self.arm_bearing_r}')
        print(f'step_r:{self.arm_step_r}')
        print(f'cone_medial:{cone_medial}')
        print(f'cone_distal:{cone_distal}')
        print(f'arm_bush_r:{arm_bush_r}')
        profile = (
            wp
            # clockwise from bottom right
            .moveTo(0, 0)
            .lineTo(0, arm_length)
            .lineTo(self.arm_bearing_r, arm_length)
            .lineTo(self.arm_bearing_r, self.bearing_step_Y)
            .lineTo(self.arm_step_r, self.bearing_step_Y)
            .lineTo(self.arm_step_r, cone_distal)
            .lineTo(arm_bush_r, cone_medial)  # the diagonal
            .lineTo(arm_bush_r, 0)
            .close()
        )
        nibs = (
            cq.Workplane("XY", (0, 0, - self.bearing_step_Y))
            .workplane(invert=True)
            .polygon(
                self.bearing_nibs_count_inner,
                self.arm_bearing_r * 2,  # diameter, sheesh
                forConstruction=True
            )
            .vertices()
            .circle(self.bearing_interference_inner)
            .extrude(self.bearing_width)
            .edges()
            .fillet(self.bearing_interference_outer - 0.01)
        )
        return profile + nibs

    def _draw_spine_profile(self, wp):
        """Center spine profile.

        Corners are rounded (too hard to draw in ASCII).
        Sketch is half from bottom center clockwise, to be mirrored.
        Left edge is Y=0.

                    //-------\
                    //        \
                    //    +    \
                    //         |
                    //         |
                    //         |
                    //---------/
        """
        outer_y = self.roller_center_height + (self.roller_od / 2)
        outer_x = self.roller_center_spacing / 2 + self.roller_od / 2
        print(f'outer_y:{outer_y}')
        print(f'outer_x:{outer_x}')
        return (
            wp
            .lineTo(0, outer_y)
            .lineTo(outer_x - (self.roller_od/2), outer_y)
            .radiusArc((outer_x, outer_y - (self.roller_od/2)), self.roller_od/2)
            .lineTo(outer_x, 0)
            .close()
            .workplane(invert=True)
            .mirrorY()
            .workplane(invert=True)
        )
#            .edges(">Y and >X")
#            .fillet(self.roller_od / 2)
#            .edges("<Y and >X")
#            .fillet(2)  # no spec, just soften these

    def _draw_leg_profile(self, wp):
        """Spine anti-tippy-jam legs.

        Not intended for locating, let the roller ends locate side to side and
        the spool itself locate front to back. Just rounded rectangles,
        mirrored about Y=0 (left side of diagram) and merged into spine at
        center, flush with bottom.

          //------------------------\
          //                        |
          //------------------------/

        """
        h = self.leg_fillet_r
        w = self.roller_overall_width / 2 - self.box_taper / 2
        print(f'h:{h}')
        print(f'w:{w}')
        return (
            wp
            .lineTo(0, h)
            .lineTo(w, h)
            .radiusArc((w - self.leg_fillet_r, 0), self.leg_fillet_r)
            .close()
            .workplane(invert=True)
            .mirrorY()
            .workplane(invert=True)
        )

    def spine(self):
        """One-piece base supporting four rollers on arms. Skateboard
        bearings fit the outer arm ends, aligned with the expected position
        of the filament reel rim; the inboard edges just bush against
        the inner surface of the arms. Intended to be printed from the side
        with supports for the overhang (one side of the spine).
        """
        arm = (
            self._draw_arm_profile(
                cq.Workplane("XZ")
            )
            .revolve(360, (0, 0), (0, 1))
            .edges()
            .fillet(self.arm_fillet_r)
        )
        two_arms = arm.add(arm.rotate((0, 0, 0), (1, 0, 0), 180))
        two_arms_A = two_arms.translate((-self.roller_center_spacing/2, self.roller_center_height, 0))
        two_arms_B = two_arms.translate(( self.roller_center_spacing/2, self.roller_center_height, 0))
        four_arms = two_arms_A.add(two_arms_B)

        legs = (
            self._draw_leg_profile(
                cq.Workplane("YZ")
            )
            .extrude(self.leg_thickness)
            .edges()
            .fillet(1.4)  # just soften things a bit
            .rotate((0,0,0), (1,0,0), 90)
            .rotate((0,0,0), (0,0,1), 180)
        )
        #two_legs = (
        #    leg
        #    .rotate((0,0,0), (1,0,0), 90)
        #    .add(leg.rotate((0, 0, 0), (0, 1, 0), 180))
        #)

        block = (
            self._draw_spine_profile(
                cq.Workplane("XY")
                .workplane(-self.spine_width / 2)
            )
            .extrude(self.spine_width)
            .edges()
            .fillet(1)
        )
        return block.add(legs).add(four_arms)
