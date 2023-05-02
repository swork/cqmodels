import types
import math
import cadquery as cq
import cqmodel.util

def instances():
    return [
        'CenterBlock.sheave',
        'CenterBlock.race',
        'CenterBlock.sheave_bolt_space_sym',
        'CenterBlock.nut_space_endwise',
        #'CenterBlock.nut_space_sidewise',
        'CenterBlock.block',
        #'CenterBlock.sheave_tower_cars'  # segfault in here somewhere
    ]

def mm(x):
    return x

def degrees(x):
    return x

def inches(x):
    return x * 25.4

class CenterBlock:
    """A double-block at the centerline of the cockpit turning the jib-track
    adjusters forward.

    (Or maybe a bigger consolidated block for all the control line sheaves.)

    Two lines cross, so offset the two blocks vertically, and adjust axle
    angles to lead to cleats. The lines are near enough horizontal going
    forward and parallel to the centerline.

    See file://bearing.jpg for bearing geometry overview.

    """
    def __init__(self):
        self.block_height_from_base = inches(2.0)
        self.block_base_length = inches(2.0)
        self.block_wing_overlap = inches(0.5)
        self.block_forward_angle = degrees(15)
        self.block_inner_width = inches(0.70)
        self.block_outer_width = inches(1.05)
        self.wing_thickness = mm(2.0)
        self.block_z_from_vertical = degrees(18)
        self.rolling_radius = mm(20)  # The radius made by the center of the line going around the roller
        self.sheave_line_center_overhang = mm(0)  # wings at line sides, positive above line center
        self.line_notch_arc_angle = degrees(90)  # advise <=90 so FDM overhangs remain <=45
        self.line_radius = mm(4)
        self.sheave_line_radius_clearance = mm(0)  # additional radius at sheave arc
        self.block_line_radius_clearance = mm(2)  # additional radius at block
        self.bearing_ball_radius = mm(1.5)
        self.ball_anti_fallthrough_percent = 20
        self.bearing_race_contact_clearance = mm(0.0)  # only to roller race, assuming zero at inner race
        self.axle_radius = mm(4)
        self.sheave_thickness = mm(14.0)
        self.sheave_cheek_clearance = mm(1.0)  # mirrored, so per side
        self.roller_lip_radius = mm(0.7)
        self.ball_circle_radius = mm(12)
        self.ball_center_inset = self.bearing_ball_radius + mm(1.5)  # ball center from cheek
        self.race_axle_clearance = mm(0.15)  # radius, so per side
        self.block_axle_clearance = mm(0.15)  # addl radius
        self.race_center_clearance = mm(0.0)  # on both races so 2x this. Neg for interference
        self.race_arc_radius_line_tilt = degrees(60)  # from parallel to axle
        self.inner_race_arc_center_offset = mm(0.75)  # along tilted line
        self.outer_race_arc_center_offset = mm(0.75)  # along tilted line
        self.roller_race_inner_tangent_angle_inside_tilt = degrees(15)
        self.sheave_end_clearance = mm(1)  # past sheave_largest_radius

        self.nut_face_depth = mm(3)  # meat to tighten against
        self.bolt_head_face_depth = mm(3)  # meat to tighten against
        self.bolt_head_face_angle = 90
        self.bolt_head_hole_radius = mm(8)
        self.bolt_head_hole_clearance = inches(12.0)  # way big
        self.bolt_clearance_past_nut = inches(12.0)  # way big

        self.nut_height = mm(6)
        self.nut_height_clearance = mm(0.5)
        self.nut_flat_count = 6
        self.nut_flat_width = mm(14)
        self.nut_flat_width_clearance = mm(0.2)


    def _bearing_params(self):
        """Common calculations for roller and race, locating the balls.

        Race arc centers lie on an angled line (cone when rotated) passing
        through the center of the ball bearings, offset from the center by
        an amount that makes the race arcs bigger than the ball surfaces.
        The angle of the line is more than 45 degrees from the axle, in
        order to keep worst-case overhang angles in the roller low enough
        to avoid support requirements (which might mess up the bearing race
        surface, though maybe a single-wall cylinder of support for the
        outer edge wouldn't be too bad).

        """
        r = types.SimpleNamespace()

        n = self.ball_circle_radius * 2 * math.pi / (self.bearing_ball_radius * 2)
        print(f'{int(n)} balls fit with a gap of {round(n - int(n), 2)} balls.')

        r.ball_center_x = self.ball_circle_radius
        r.ball_center_y = round(
            (self.sheave_thickness / 2)
            + self.sheave_cheek_clearance
            - self.ball_center_inset,
            3
        )

        # The arc defining the inner race surface
        r.inner_arc_center_y = round(
            r.ball_center_y
            - (
                math.cos(math.radians(self.race_arc_radius_line_tilt))  # opposite over hypoteneuse
                * self.inner_race_arc_center_offset
            ),
            3
        )
        r.inner_arc_center_x = round(
            r.ball_center_x
            + (
                math.sin(math.radians(self.race_arc_radius_line_tilt))  # adjacent over hypoteneuse
                * self.inner_race_arc_center_offset
            ),
            3
        )
        r.inner_arc_radius = round(
            self.bearing_ball_radius
            + self.inner_race_arc_center_offset,
            3
        )

        r.sheave_race_arc_center_y = round(
            r.ball_center_y
            + (
                math.cos(math.radians(self.race_arc_radius_line_tilt))  # opp over hyp
                * self.outer_race_arc_center_offset
            ),
            3
        )
        r.sheave_race_arc_center_x = round(
            r.ball_center_x
            - (
                math.sin(math.radians(self.race_arc_radius_line_tilt))  # adj over hyp
                * self.outer_race_arc_center_offset
            ),
            3
        )
        r.sheave_race_arc_radius = round(
            self.bearing_ball_radius
            + self.outer_race_arc_center_offset,
            3
        )

        # With arc centers and radii in hand, find the start and end points.
        # Inner race, ends are where arc tangent lines are parallel/perp to axle:
        r.inner_arc_inner_end_x = round(
            r.inner_arc_center_x
            - r.inner_arc_radius,
            3
        )
        r.inner_arc_inner_end_y = round(
            r.inner_arc_center_y,
            3
        )
        r.inner_arc_outer_end_x = round(
            r.inner_arc_center_x,
            3
        )
        r.inner_arc_outer_end_y = round(
            r.inner_arc_center_y
            + r.inner_arc_radius,
            3
        )
        r.sheave_race_arc_outer_end_x = round(
            r.sheave_race_arc_center_x
            + r.sheave_race_arc_radius,
            3
        )
        r.sheave_race_arc_outer_end_y = round(
            r.sheave_race_arc_center_y,
            3
        )

        # outer arc inner end is tangent at an arbitrary angle. FDM wants
        # that angle to stay below 45 degrees from the axle to avoid
        # supporting an overhang, and 45 is probably the target but let's
        # parameterize it.
        r.tangent_angle = round(
            self.race_arc_radius_line_tilt
            - self.roller_race_inner_tangent_angle_inside_tilt,
            3
        )
        r.sheave_race_arc_inner_end_x = round(
            r.sheave_race_arc_center_x
            + (
                math.sin(math.radians(r.tangent_angle))
                * r.sheave_race_arc_radius
            ),
            3
        )
        r.sheave_race_arc_inner_end_y = round(
            r.sheave_race_arc_center_y
            - (
                math.cos(math.radians(r.tangent_angle))
                * r.sheave_race_arc_radius
            ),
            3
        )
        r.sheave_largest_radius = (
            self.rolling_radius
            + self.sheave_line_center_overhang
        )

        return r

    def race(self):
        """Inner race. Draw +x+y and revolve around Y into solid.
        Constraints include:

        1. ball must be inside cheek

        2. contact point should be close to the 45-degree mark

        3. an inward cylindrical boss against the axle must provide less
        total clearance than the ball diameter, to help with assembly.

        To meet these, consider a race arc same radius as the ball with
        ball grazing the cheek. Move the center away from the cheek by
        inner_race_ball_cheek_clearance (making a cylindrical flat normal
        to the block cheek between the cheek and the race arc), then move
        it 45-degrees further inward and away from the axle to make the arc
        radius bigger than the ball radius while maintaining the optimal
        ball-to-race contact point (which requires the roller getting this
        optimal too). Carry a cylinder about the axle inward far enough
        that the inner race can be lifted outward enough to fit the balls
        in during assembly without them falling into the middle.
        (Trial-and-error this rather than calculate this.)
        """
        r = self._bearing_params()
        print(r)
        race_axle_cylinder_radius = self.axle_radius + self.race_axle_clearance
        race_cheek_y = (self.sheave_thickness/2)
        try:
            assert race_cheek_y > r.inner_arc_outer_end_y
        except:
            print(f'Whoops, cheek:{race_cheek_y} vs arc_y:{r.inner_arc_outer_end_y}')
            raise
        race = (
            cq.Workplane("XZ")

            # inner surface of axle clearance cylinder at middle of race
            .moveTo(
                race_axle_cylinder_radius,
                self.race_center_clearance
            )

            # up to cheek along axle
            .lineTo(
                race_axle_cylinder_radius,
                race_cheek_y
            )

            # out to extent of inner race lip
            .lineTo(
                r.inner_arc_outer_end_x,
                race_cheek_y
            )

            # inward parallel to axle to make a squared-off lip
            .lineTo(
                r.inner_arc_outer_end_x,
                r.inner_arc_outer_end_y
            )

            # the arc of the race itself
            .radiusArc(
                (
                    r.inner_arc_inner_end_x,
                    r.inner_arc_inner_end_y
                ),
                -r.inner_arc_radius
            )

            .lineTo(
                r.inner_arc_inner_end_x,
                self.race_center_clearance
            )

            .close()

            .revolve(
                360,
                (0, 0, 0),
                (0, 1, 0)
            )
        )
        return race

    def sheave(self):
        """Wheel part of block. Draw +x+y portion of profile, mirror into
        +x-y, and revolve around Y into the solid. Bearing race radius is
        arbitrary, trading off friction (too close to ball diameter, so
        parts rub) and contact point strain (too far from ball diameter, so
        point of contact impresses).
        """
        r = self._bearing_params()

        # The gap between inner race and sheave is sized so the balls can't fall through.
        # The surface from this inside cylinder to the race arc is a "tangent extension"
        # from the race arc. FDM wants this to be closer to vertical than 45 degrees
        # (considered with the sheave on its flat side).
        sheave_inner_radius = round(
            r.inner_arc_inner_end_x
            + (
                self.bearing_ball_radius
                * (1 - (self.ball_anti_fallthrough_percent/100))
            ),
            3
        )
        tangent_extension_x_distance = (
            r.sheave_race_arc_inner_end_x
            - sheave_inner_radius
        )
        tangent_extension_y_distance = (
            math.tan(math.radians(r.tangent_angle))
            * tangent_extension_x_distance
        )
        print(f'rolling_radius:{self.rolling_radius} sheave_inner_radius:{sheave_inner_radius} tangent_extension_distance:({round(tangent_extension_x_distance, 2)},{round(tangent_extension_y_distance)})')
        try:
            assert(r.sheave_race_arc_inner_end_y > tangent_extension_y_distance)
        except:
            print(f'Whoops, inner_y:{r.sheave_race_arc_inner_end_y} vs ext:{tangent_extension_y_distance}')
            raise

        # FDM also wants the outer notch of the sheave where the line rides to
        # stay within 45 of vertical with the sheave on its side, so we'll make
        # the notch out of an arc at the bottom with tangent extensions up to
        # the outer edge of the sheave.
        line_notch_arc_center_x = self.rolling_radius
        line_notch_arc_center_y = 0  # mid-plane of sheave
        # self.line_notch_arc_angle
        line_notch_arc_radius = self.line_radius + self.sheave_line_radius_clearance

        line_notch_arc_inner_end_x = self.rolling_radius - self.line_radius  # .sheave_line_radius_clearance doesn't affect the bottom of the notch
        line_notch_arc_inner_end_y = 0  # duh, middle plane when revolved
        line_notch_arc_outer_end_x = self.rolling_radius - (
            math.sin(math.radians(self.line_notch_arc_angle/2))
            * line_notch_arc_radius
        )
        line_notch_arc_outer_end_y = (
            math.cos(math.radians(self.line_notch_arc_angle/2))
            * line_notch_arc_radius
        )
        # line_arc_tangent_extension_x is r.sheave_largest_radius
        line_notch_arc_tangent_extension_y = (
            math.tan(math.radians(90-self.line_notch_arc_angle/2))
            * (r.sheave_largest_radius - line_notch_arc_outer_end_x)
        ) + line_notch_arc_outer_end_y
        print(f'line_notch_arc_center:({line_notch_arc_center_x},{line_notch_arc_center_y}) line_notch_arc_radius:{line_notch_arc_radius} line_notch_arc_outer_end:({line_notch_arc_outer_end_x},{line_notch_arc_outer_end_y}) tangent_extension_y:{line_notch_arc_tangent_extension_y}')
        assert(line_notch_arc_outer_end_y < self.sheave_thickness / 2)
        assert(line_notch_arc_outer_end_x < r.sheave_largest_radius)

        sheave = (
            cq.Workplane("XZ")

            # inner surface of sheave cylinder, facing cylindrical part of
            # inner race, close enough that balls can't fall in during assembly
            .moveTo(
                (
                    r.sheave_race_arc_inner_end_x
                    - tangent_extension_x_distance
                ),
                0
            )

            # up (+Y) to beginning of ball race arc tangent extension
            .lineTo(
                (
                    r.sheave_race_arc_inner_end_x
                    - tangent_extension_x_distance
                ),
                (
                    r.sheave_race_arc_inner_end_y
                    - tangent_extension_y_distance
                )
            )

            # up and out to arc
            .lineTo(
                r.sheave_race_arc_inner_end_x,
                r.sheave_race_arc_inner_end_y
            )

            # the race arc
            .radiusArc(
                (
                    r.sheave_race_arc_outer_end_x,
                    r.sheave_race_arc_outer_end_y
                ),
                - r.sheave_race_arc_radius  # counterclockwise
            )

            # up to cheek-facing plane of sheave
            .lineTo(
                r.sheave_race_arc_outer_end_x,
                self.sheave_thickness/2
            )

            # out to sheave lip
            .lineTo(
                r.sheave_largest_radius,
                self.sheave_thickness/2
            )

            # V-notch at outer end. Outer lip
            .lineTo(
                r.sheave_largest_radius,
                line_notch_arc_tangent_extension_y
            )

            # diagonal to arc at middle
            .lineTo(
                line_notch_arc_outer_end_x,
                line_notch_arc_outer_end_y
            )

            # the arc itself
            .radiusArc(
                (
                    line_notch_arc_inner_end_x,
                    line_notch_arc_inner_end_y
                ),
                - line_notch_arc_radius  # counterclockwise
            )

            # for profile: replace all following with .close().extrude(1)
            .mirrorX()  
            .revolve(
                360,
                (0, 0, 0),
                (0, 1, 0)
            )

            # Troubleshoot: see reference 0,0,0 at center of sheave.
            # Z is parallel to the axle.
            # .sphere(16)
        )

        return sheave

    def sheave_bolt_space_asym(self):
        """Negative space for the sheave and races defined above, along with an
        axle bolt and nuty.

        """
        r = self._bearing_params()

        bolt_hole_radius = self.axle_radius + self.block_axle_clearance

        sheave_space_bottom_y = - (
            self.sheave_thickness / 2
            + self.sheave_cheek_clearance
        )
        sheave_space_top_y = (
            self.sheave_thickness / 2
            + self.sheave_cheek_clearance
        )
        sheave_space_outer_x = (
            r.sheave_largest_radius
            + self.sheave_end_clearance
        )
        bolt_head_face_inner_y = (
            sheave_space_top_y
            + self.bolt_head_face_depth
        )
        bolt_head_face_outer_y = (
            (
                math.cos(math.radians(self.bolt_head_face_angle))
                * (
                    self.bolt_head_hole_radius
                    - bolt_hole_radius
                )
            )
            + bolt_head_face_inner_y
        )
        line_space_radius = (
            self.line_radius
            + self.block_line_radius_clearance
        )

        # Two pieces, first the bolt-and-sheave space by revolution,
        # then options for nut insertion from end or side.
        # Origin at center of sheave.
        bolt = (
            cq.Workplane("XZ")
            .lineTo(
                0,
                - self.bolt_clearance_past_nut
            )
            .lineTo(
                bolt_hole_radius,
                - self.bolt_clearance_past_nut
            )
            .lineTo(
                bolt_hole_radius,
                sheave_space_bottom_y
            )
            .lineTo(
                sheave_space_outer_x,
                sheave_space_bottom_y
            )
        )

        # Only step in/out if necessary
        if abs(line_space_radius - sheave_space_bottom_y) > mm(0.1):
            bolt = (
                bolt
                .lineTo(
                    sheave_space_outer_x,
                    -line_space_radius
                )
            )

        bolt = (
            bolt
            .radiusArc(
                (
                    sheave_space_outer_x,
                    line_space_radius
                ),
                - line_space_radius  # counterclockwise
            )
        )

        if abs(line_space_radius - sheave_space_top_y) > mm(0.1):
            bolt = (
                bolt
                .lineTo(
                    sheave_space_outer_x,
                    sheave_space_top_y
                )
            )

        bolt = (
            bolt
            .lineTo(
                bolt_hole_radius,
                sheave_space_top_y
            )

            .lineTo(
                bolt_hole_radius,
                bolt_head_face_inner_y
            )

            # angled so we can work with flat-head screws, but usu. 90
            .lineTo(
                self.bolt_head_hole_radius,
                bolt_head_face_outer_y
            )

            # way up intended past surface of whatever we're embedded in
            .lineTo(
                self.bolt_head_hole_radius,
                self.bolt_head_hole_clearance
            )

            .lineTo(
                0,
                self.bolt_head_hole_clearance
            )

            .close()

            # for profile: replace .revolve(...) with .extrude(1)
            .revolve(
                360,
                (0, 0, 0),
                (0, 1, 0)
            )

            # TODO: this sphere shows origin at center of mass, not useful. I
            # haven't found a way to adjust it back to the global 0,0,0 I
            # started with, which seems to me a most basic operation.
            #.sphere(18)
        )
        return bolt

    def sheave_bolt_space_sym(self):
        """Negative space for the sheave and races defined above, along with an
        axle bolt and nuty.

        """
        r = self._bearing_params()

        bolt_hole_radius = self.axle_radius + self.block_axle_clearance

        sheave_space_top_y = (
            self.sheave_thickness / 2
            + self.sheave_cheek_clearance
        )
        sheave_space_outer_x = (
            r.sheave_largest_radius
            + self.sheave_end_clearance
        )
        bolt_head_face_inner_y = (
            sheave_space_top_y
            + self.bolt_head_face_depth
        )
        bolt_head_face_outer_y = (
            (
                math.cos(math.radians(self.bolt_head_face_angle))
                * (
                    self.bolt_head_hole_radius
                    - bolt_hole_radius
                )
            )
            + bolt_head_face_inner_y
        )
        line_space_radius = (
            self.line_radius
            + self.block_line_radius_clearance
        )

        # Two pieces, first the bolt-and-sheave space by revolution,
        # then options for nut insertion from end or side.
        # Origin at center of sheave.
        hole = (
            cq.Workplane("XZ")
            .moveTo(sheave_space_outer_x + line_space_radius, 0)
            .radiusArc(
                (
                    sheave_space_outer_x,
                    line_space_radius
                ),
                - line_space_radius  # counterclockwise
            )
        )

        if abs(line_space_radius - sheave_space_top_y) > mm(0.1):
            hole = (
                hole
                .lineTo(
                    sheave_space_outer_x,
                    sheave_space_top_y
                )
            )

        hole = (
            hole
            .lineTo(
                bolt_hole_radius,
                sheave_space_top_y
            )

            .lineTo(
                bolt_hole_radius,
                bolt_head_face_inner_y
            )

            # angled so we can work with flat-head screws, but usu. 90
            .lineTo(
                self.bolt_head_hole_radius,
                bolt_head_face_outer_y
            )

            # way up intended past surface of whatever we're embedded in
            .lineTo(
                self.bolt_head_hole_radius,
                self.bolt_head_hole_clearance
            )

            .lineTo(
                0,
                self.bolt_head_hole_clearance
            )

            .lineTo(0, 0)

            .close()

            .revolve(
                180,
                (0, 0, 0),
                (0, 1, 0)
            )
        )

        andrestofcircle = hole.mirror("XZ", union=True)
        andotherhalf = andrestofcircle.mirror("XY", union=True)
        andotherhalf.findSolid().fix()
        return andotherhalf

    def nut_space_endwise(self):
        nut_space_top_y = (
            self.sheave_thickness / 2
            + self.sheave_cheek_clearance
            + self.nut_face_depth
        )
        nut_flat_space = (
            self.nut_flat_width
            + self.nut_flat_width_clearance
        )
        space = (
            cq.Workplane("XY")
            .polygon(
                self.nut_flat_count,
                nut_flat_space,
                circumscribed=True
            )
            .extrude( - inches(13))  # a long way
        )
        return space

    def _draw_block_inner_profile(self, wp):
        return (
            wp
            .lineTo(
                self.block_base_length,
                0
            )
            .lineTo(
                self.block_base_length,
                self.block_height_from_base
            )
            .lineTo(
                (
                    math.tan(math.radians(self.block_forward_angle))
                    * self.block_height_from_base
                ),
                self.block_height_from_base
            )
            .close()
        )

    def block(self):
        wp = cq.Workplane("YZ")
        self._draw_block_inner_profile(wp)
        side_profile_inner = (
            wp
            .extrude(self.block_inner_width)
        )
        return side_profile_inner

    def _tower(self, baseX, baseY, topX, topY, Z, bolt_offset_from_end):
        cqmodel.util.infoize()
        tower = (
            cq.Workplane("XY")
            .rect(baseX, baseY)
            .workplane(Z)
            .rect(topX, topY)
            .loft()
            .edges("|X and (not <Z)")
#            .fillet(bolt_offset_from_end)
            #.edges(">Z and <Y")
            #.fillet(bolt_offset_from_end)
        )

        # print(f'tower:{tower}')
        tower = (
            tower
            .edges("not(<Z)")
#            .fillet(5)
        )
        print(f'tower2:{tower}')

        sheave_hole = (
            cq.Workplane("XY")
            .add(self.sheave_bolt_space_sym().findSolid())
            .rotate(cq.Vector(), (0, 1, 0), 90)
            .translate((0, 0, Z - bolt_offset_from_end))
        )
        # print(f'hole:{sheave_hole}')
        tower = (
            tower
            .cut(sheave_hole)
            # .edges()  # all that remain
            # .fillet(0.04)
        )
        tower.findSolid().fix()
        # print(f'tower3:{tower}')
        return tower

    def sheave_tower_cars(self):
        return self._tower(28, 30, 23, 25, 45, 10)
