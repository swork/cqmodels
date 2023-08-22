"""CQ model of a replacement link for my beach house window blinds. Dims in mm"""

import cadquery as cq
from cadquery import Vector
import math
from types import SimpleNamespace as ns

SQRT2 = 1.414

class PARAMS:
    blade_pin_Z = 4
    blade_pin_diameter = 2.35
    overall_Z = 4.8
    blade_plate_Z = 0.7
    pin_plate_Z = 2.3
    socket_plate_Z = 2.5
    blade_pin_from_male_end_X = 31.3 
    blade_pin_from_straight_side_Y = 11.0 - 7.6
    clearance_from_male_end_min_X = 19.8
    clearance_from_male_end_max_X = 44.3
    clearance_scoop_narrowest_Y = 5.5
    overall_Y = 7.6

    # width of narrower connector part
    connector_size_Y = 5.2
    # thickness of connector, flush with max-Z
    connector_size_Z = 2.5
    # length of connector, including end hook
    connector_size_X = 15.2
    # length of end hook (part of connector_size_X)
    connector_hook_X = 2.5
    connector_male_end_chamfer = 2.5 * SQRT2

    connector_pin_female_Y = 1.0
    connector_pin_female_X = 3.8
    connector_female_X = 12.5
    connector_female_socket_to_end_X = 1.4
    connector_female_slot_X = 4.0
    connector_female_slot_gap_X = 2.8
    connector_female_space_X = 2.7
    connector_pin_male_Y = 1.0
    connector_pin_male_X = 3.4
    connector_male_indent_X = 12.5
    connector_male_pin_indent_X = 0.5
    connector_male_pin_gap_X = 3.5
    connector_lip_Z = 0.2
    connector_lip_Y = 0.2
    overall_X = 93.9


def instance(p=PARAMS):

    connector_
    connector = (cq.Workplane("XY")
                 .faces("+Z")
                 .invert()
                 .moveTo(0, p.overall_Y / 2)
                 .box(p.connector_size_X, p.connector_size_Y, p.connector_size_Z,
                      centered = (False, True, False))
                 .faces("-Z")
                 .moveTo()
                 
                 )

    basic_bar = (cq.Workplane("XY")
                 .box(p.overall_X, p.overall_Y, p.overall_Z, centered=False)

                 # scoop for blind clearance
                 .workplane().faces("-Z")
                 .moveTo(p.overall_X - p.clearance_from_male_end_min_X, 0)
                 .threePointArc(Vector(p.overall_X - p.blade_pin_from_male_end_X,
                                       p.overall_Y - p.clearance_scoop_narrowest_Y, 0),
                                Vector(p.overall_X - p.clearance_from_male_end_max_X,
                                       0, 0))
                 .close()
                 .cutThruAll()

                 # female main hollow
                 .moveTo((p.overall_Y - p.connector_female_inside_Y) / 2,
                         p.connector_female_plate_Z)
                 .rect(p.connector_female_inside_Y,
                       p.overall_Z - p.connector_female_plate_Z - p.connector_lip_Z)
                 .cutBlind(p.connector_female_X)
                 )

    result = basic_bar
    # 
    # xmax_y0_vertices = basic_bar.faces("+X").vertices("<Y")
    # xmax_y0_z0_vertex = (basic_bar.faces("-Z").vertices(">X")
    # plate = (
    #          .faces
    #          )


    #              .faces("+X").vertices()
    #              )


    return result

