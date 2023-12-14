import cadquery as cq

def instance():
    bar_diameter = 22
    clamp_width = 10
    stub_height_above_bar = 22

    # bike's pitch, yaw, roll (so "pitch axis" means handlebar axis
    # and "yaw axis" means steer tube axis, sort of)
    offset_stub_along_pitch_axis = 6
    offset_stub_along_roll_axis = 15
    offset_stub_along_yaw_axis = 15

    # derived
    stub_extrude = stub_height_above_bar + offset_stub_along_yaw_axis

    m = (
        cq.Workplane("XY") # middle of handlebar at mount point, plan view

        # The mounting stub
        .circle(bar_diameter / 2)
        .extrude(stub_extrude)
        .edges()
        .fillet(1)

        # The handlebar clamp ring
        .rotate((0, 0, stub_extrude/2),
                (0, 1, stub_extrude/2),
                90)  # this rotates the part, not the reference plane
        .workplane(offset_stub_along_pitch_axis)
        .moveTo(offset_stub_along_yaw_axis, offset_stub_along_roll_axis)
        .circle(bar_diameter / 2 + 2)
        .extrude(-clamp_width)
        .moveTo(offset_stub_along_yaw_axis, offset_stub_along_roll_axis)
        .circle(bar_diameter / 2)
        .cutThruAll()

        # hole to tighten clamp \
        .faces(">X")
        .workplane()
        .moveTo(-5, -(clamp_width/2))
        .cboreHole(diameter=2.4, cboreDiameter=8, cboreDepth=1, depth=30)
    )

    # Stress spreaders. Found the edge indices by trial and error.
    edges = m.edges().all()  # workplanes
    edge_objs = list(map(lambda x: x.objects[0], edges))
    m = m.newObject([edge_objs[i] for i in (4,5,6,21,22,23,24,25)]).fillet(1)


    # Gap to tighten clamp
    g = (
        cq.Workplane("YZ")
        .workplane(12)  # offset
        .moveTo(0, 18)
        .circle(bar_diameter / 2 + 1)
        .extrude(2)
    )

    return m - g
