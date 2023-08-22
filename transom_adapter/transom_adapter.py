import math
import cadquery as cq

def inches(x):
    return x * 25.4

def radius_of_sagitta(chord, height):
    """
    R = (h/2) + (c^2 / 8h)
    """

    return (height / 2) + (chord * chord / 8 * height)

def transom_adapter_starboard():
    """
    ___
    ) /
    )/

    Oddly, cutting holes in the solid screws up the curved face - it
    becomes a weird set of triangles, with a straight spine between
    the holes (not even the center of the holes).
    """
    #arc_sag = inches(0.25)
    #arc_sag = inches(0.07)
    #arc_sag = inches(0.17)
    arc_sag = inches(0.21)
    min_thickness = inches(0.25)
    max_thickness = inches(2)
    face_height = inches(9)

    a = (
        cq.Workplane("XY")
        .line(0, inches(9))
        .line(inches(0.25), 0)
        .sagittaArc((max_thickness, 0),
                    -arc_sag)

        .close()
        .extrude(inches(2))

        .edges("<YZ").fillet(inches(0.5))
        .edges(">Y and <Z").fillet(inches(0.5))

        .faces("<X").vertices(">YZ").workplane()

        .moveTo(inches(-0.75), inches(0.75))
        .hole(inches(0.375))
        .moveTo(inches(-5.75), inches(0.75))
        .hole(inches(0.375))
    )
    return a

def transom_adapter_port():
    """
    ___
    ) /
    )/

    See _starboard for notes; build this by cutting the arc away
    from a box. (Outcome: exactly the same, hmm.)
    """
    arc_sag = inches(0.21)
    max_thickness = inches(2)
    min_thickness = inches(0.25)
    face_height = inches(9)

    # transom curve
    #thick_diff = max_thickness - min_thickness
    #chord = math.sqrt(
    #    thick_diff * thick_diff
    #    + face_height * face_height
    #)
    #bc_radius = radius_of_sagitta(chord, arc_sag)
    #print(f'chord:{chord/25.4} and height:{arc_sag/25.4} -> radius:{bc_radius/25.4}')

    # locate the arc center of the transom curve in the YZ plane
    lower_arc_point = (0, min_thickness)
    upper_arc_point = (-face_height, max_thickness)

    # x^2 + y^2 = r^2 for both points, two solutions
    #centers = circle_intersections()
    #(lower_arc_point[0] * lower_arc_point[0]) + (lower_arc_point[1] * lower_arc_point[1])
    # arc_centerline_slope = (
    #     (upper_arc_point[0] - lower_arc_point[0])
    #     / (upper_arc_point[1] - lower_arc_point[1])
    # )

    # big_cylinder = (
    #     cq.Workplane("XY")
    #     .workplane(offset=bc_radius - inches(3.75))
    #     .move(0, -inches(110))
    #     .cylinder(inches(1), bc_radius,
    #               direct=(1, 0, 0),
    #               centered=(True, True, False))
    # )

    box = (
        cq.Workplane("XY")
        .box(inches(2), face_height, inches(2),
             centered=False)
        .edges("|Z and >X")
        .fillet(inches(0.5))
    )

    drillings = (
        cq.Workplane("XY")
        .pushPoints(
            [
                (inches(1.25), face_height - inches(0.75)),
                (inches(1.25), face_height - inches(5.75))
            ]
        )
        .cylinder(inches(5), inches(0.375) / 2)
    )

    drilled_cut_curved = (
        (box - drillings)
        .faces("<X").workplane()
        .moveTo(*lower_arc_point)
        .sagittaArc(upper_arc_point, arc_sag)
        .line(face_height, 0)
        .close()
        .cutThruAll() #.extrude(inches(1)) 
    )

    return drilled_cut_curved

def instances():
    return [
        "transom_adapter_starboard",
        "transom_adapter_port",
    ]

