"""CQ model of a concrete form for leg corner of a heavy work table."""

import cadquery as cq
import math

def mm(mm: float) -> float:
    return mm

def inches(mm: float) -> float:
    return mm * 25.4

PARAMS = {
    'form_wall_thickness': mm(1),
    'shelf_width': inches(2.0),   # overlapping bottom of tabletop form, after a fillet
    'table_thickness': inches(4.0),
    'leg_stub_diameter': inches(7.0),
    'leg_stub_height': inches(5.0),
}

def instance(p=PARAMS):

    # Derived
    leg_stub_radius = p['leg_stub_diameter'] / 2
    enough_table_X = p['leg_stub_diameter'] * 3
    enough_table_Y = enough_table_X

    # We'll shell over the socket we construct below, and concrete will see the
    # shell side - so subtract out wall thickness
    leg_socket_dim = inches(3.5) - (p['form_wall_thickness'] * 2)

    # Table walls
    inner_radius = leg_stub_radius
    outer_radius = inner_radius + p['form_wall_thickness']
    walls = (cq.Workplane("XY")
             .workplane(p['leg_stub_height'] - inches(1.0))
             .cylinder(p['table_thickness'] + inches(1.0),
                       leg_stub_radius + p['form_wall_thickness'])
             .circle(leg_stub_radius)
             .cutThruAll()

             # Cut away the bits that would be inside the table
             .faces(">Z")
             .workplane()  # - p['table_thickness'])
             .line(0, -leg_stub_radius * 2)
             .line(leg_stub_radius * 2, 0)
             .line(0, leg_stub_radius * 4)
             .line(-leg_stub_radius * 4, 0)
             .line(0, -leg_stub_radius * 2)
             .close()
             .cutThruAll()  # Blind(p['table_thickness'])
             )

    pos_box_1 = (cq.Workplane("XZ")
                 .workplane(inner_radius)
                 .moveTo(0, inches(2.5))
                 .box(leg_stub_radius + inches(1),
                      p['table_thickness'],
                      p['form_wall_thickness'],
                      centered=(False, False, False)
                      )
                 )

    neg_box_1 = (cq.Workplane("XZ")
                 .workplane(outer_radius)
                 .box(p['leg_stub_diameter'] * 3,
                      p['leg_stub_diameter'] * 3,
                      p['leg_stub_height'] * 3,
                      centered=(True, True, False))
                 )

    # vertical bar to support the top part of the side walls
    support1 = (cq.Workplane("XZ")
                .workplane(outer_radius)
                .moveTo(inches(4.0), inches(2.5))
                .box(2, p['table_thickness'], 2, centered=False)
                .edges("<<Z and <<Y")
                .toPending()
                .chamfer(1.999)
                )

    pos_box_2 = (cq.Workplane("YZ")
                 .workplane(-outer_radius)
                 .moveTo(0, inches(2.5))
                 .box(leg_stub_radius + inches(1),
                      p['table_thickness'],
                      p['form_wall_thickness'],
                      centered=(False, False, False)
                      )
                 )

    neg_box_2 = (cq.Workplane("YZ")
                 .workplane(outer_radius, invert=True)
                 .box(p['leg_stub_diameter'] * 3,
                      p['leg_stub_diameter'] * 3,
                      p['leg_stub_height'] * 3,
                      centered=(True, True, False))
                 )

    support2 = (cq.Workplane("YZ")
                .workplane(outer_radius, invert=True)
                .moveTo(inches(4.0), inches(-6.5))
                .box(2, p['table_thickness'], 2, centered=False)
                .edges("<<Z and <<X")
                .toPending()
                .chamfer(1.999)
                )

    stiffeners = support1 + support2

    # form_supported = (form
    #                   .faces(">>Z")
    #                   .workplane(origin=(-(outer_radius+2), inches(3.6)), invert=True)
    #                   .box(2, 2, p['table_thickness'], centered=False)
    #                   # .faces("<<Z")  # of the new box, I hope
    #                   # .edges("#Z")
    #                   # .toPending()
    #                   # .chamfer(1)  # hoping to avoid extra supports

    #                   # and again on the other wall
    #                   .faces(">>Z")
    #                   .workplane(origin=(inches(3.6), -(outer_radius)), invert=True)
    #                   .box(2, 2, p['table_thickness'], centered=False)
    #                   )



    leg = (cq.Workplane("XY")

           # Shape of the concrete leg below the table bottom, with rounded bottom edge
           .cylinder(p['leg_stub_height'],
                     leg_stub_radius)
           .faces("<<Z")
           .fillet(inches(0.5))

           # Make an indent for 4x4 leg extensions
           .faces("<<Z")
           .workplane(invert=True)
           .rect(leg_socket_dim, leg_socket_dim)
           .cutBlind(inches(2))

           # Make it into a form for that shape
           .faces(">>Z")
           .shell(p['form_wall_thickness'])

           # Make a shelf to fillet and later cut back to match up with the
           # bottom of the tabletop
           .faces(">>Z")
           .workplane()
           .cylinder(inches(0.6), leg_stub_radius * 1.5)

           # Cut out the center to match inside of form
           .faces(">>Z")
           .workplane()
           .circle(leg_stub_radius)
           .cutBlind("next")

           # Fillet the edges of the shelf
           .faces(">>Z")
           .edges()
           .fillet(inches(0.5))

           # Cut the shelf back to match bottom of the tabletop. Start off the
           # bottom, to make the washer-shaped cut wires, then cut back toward
           # the top
           .faces("<<Z")
           .workplane()
           .sketch()
           .circle(leg_stub_radius * 1.5)
           .circle(leg_stub_radius + inches(0.5), mode='s')
           .finalize()
           .cutBlind( - (p['leg_stub_height'] + inches(0.3)))
           )
    

    form = (((leg + pos_box_1 + pos_box_2) - neg_box_1) - neg_box_2) + walls + stiffeners

    return form

