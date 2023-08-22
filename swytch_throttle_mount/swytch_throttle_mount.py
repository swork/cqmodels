import cadquery as cq

def instances():
    return [
        'mount'
    ]

def mount():
    bar_diameter = 22
    clamp_width = 10
    stub_height_above_bar = 22

    # bike's pitch, yaw, roll (so "pitch axis" means handlebar axis,
    # sort of)
    offset_stub_along_pitch_axis = 6
    offset_stub_along_roll_axis = 15
    offset_stub_along_yaw_axis = 12

    m = (
        cq.Workplane("XY")

        # The mounting stub
        .circle(bar_diameter / 2)
        .extrude(stub_height_above_bar + offset_stub_along_roll_axis)

        # The handlebar clamp ring
        .rotateAboutCenter((0, 1, 0), 90)  # this rotates the part, not the reference plane
        .workplane(offset_stub_along_pitch_axis)
        .moveTo(offset_stub_along_roll_axis, offset_stub_along_yaw_axis)
        .circle(bar_diameter / 2 + 2)
        .extrude(-clamp_width)
        .moveTo(offset_stub_along_roll_axis, offset_stub_along_yaw_axis)
        .circle(bar_diameter / 2)
        .cutThruAll()

        # hole to tighten clamp
        .faces(">X")
        .workplane()
        .moveTo(-5, -(clamp_width/2))
        .cboreHole(diameter=2.4, cboreDiameter=8, cboreDepth=1, depth=30)
    )

    # Gap to tighten clamp
    g = (
        cq.Workplane("YZ")
        .workplane(12)  # offset
        .moveTo(0, 18)
        .circle(bar_diameter / 2 + 1)
        .extrude(2)
    )

    return m - g
