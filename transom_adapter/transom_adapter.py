import math
import cadquery as cq

def inches(x):
    return x * 25.4

def transom_adapter():
    """
    ___
    ) /
    )/
    """
    #arc_sag = inches(0.25)
    #arc_sag = inches(0.07)
    #arc_sag = inches(0.17)
    arc_sag = inches(0.21)
    top_displacement = inches(2)
    face_line_length = inches(9)

    bottom_angle_r = math.acos(top_displacement / face_line_length)
    bottom_tan = math.tan(bottom_angle_r)

    face_line_delta_Y = top_displacement / bottom_tan

    a = (
        cq.Workplane("XY")
        .line(0, inches(9))
        .line(inches(0.25), 0)
        .sagittaArc((top_displacement, 0),
                    -arc_sag)

        .close()
        .extrude(inches(2))

        .edges("<YZ").fillet(inches(0.5))
        .edges(">Y and <Z").fillet(inches(0.5))

        .faces("<X").vertices(">YZ").workplane()

        .moveTo(inches(-0.75), inches(0.75))
        .hole(inches(0.375))
        .moveTo(inches(-6.75), inches(0.75))
        .hole(inches(0.375))
    )
    return a

def instances():
    return [ "transom_adapter" ]

