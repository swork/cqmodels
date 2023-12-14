import cadquery as cq

def back(width):
    back = (
        cq.Workplane("XY")
        .line(0, 28)
        .radiusArc((width, 28), width//2)
        .line(0, -28)
        .close()
        .moveTo(width//2, 28)
        .circle(2)
        .extrude(2)
    )
    back.faces("<Y").tag("floorfacing")
    back.faces("<Z").tag("wallfacing")
    back.faces("<X").tag("left")
    back.faces(">X").tag("right")
#    back.faces("<Y").edges("<Z").vertices("<X").tag("pt1")
    return back

def hook(baseLength, width):
    h = (
        cq.Workplane("XZ")
        .line(0, 4 + baseLength)
        .radiusArc((width, 4 + baseLength), width//2)
        .line(-2, 0)
#        .radiusArc((2, 4 + baseLength), -2)
        .lineTo(width, baseLength)
        .lineTo(width, 0)
        .close()
        .moveTo(width//2, 4 + baseLength)
        .circle(2 + (width//2 - 4))
        .extrude(3)
    )
    h.faces("<Z").tag("wallfacing")
    h.faces("<Y").tag("floorfacing")
    h.faces(">Y").tag("topfacing")
    h.faces("<X").tag("straight")
    h.faces("<Z").edges("<X").vertices("<Y").tag("pt1")
    return h

def instance():
    cable_diameter=6  # an even number
    width = cable_diameter + 4
    low = hook(6, width)
    up = hook(4, width)  # shorter too by thickness of back
    inst = (
        cq.Assembly(back(width), name="back")
        .add(low, name="lower")
        .add(up, name="upper")
        .constrain("back?wallfacing", "lower?wallfacing", "Axis")
        .constrain("back?floorfacing", "lower?floorfacing", "Axis")
        .constrain("back?right", "lower?straight", "Axis")
        .constrain("back?wallfacing", "upper?wallfacing", "Axis")
        .constrain("back?floorfacing", "upper?topfacing", "Axis")  # upside down
        .constrain("back?right", "upper?pt1", "Point")
        .solve()
        .toCompound()
    )
    print(inst)
    return inst

