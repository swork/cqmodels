import cadquery as cq

def inch(i):
    return i * 25.4

def locator():
    x = (
        cq.Workplane("XY")
        .moveTo(0, 2)
        .radiusArc((2, 0), -2)
        .line(16, 0)
        .tangentArcPoint((2, 2))
        .line(0, 23)
        .tangentArcPoint((-5, 5))
        .line(-2.5, 0)
        .tangentArcPoint((-5, -5))
        .line(0, -10)
        .tangentArcPoint((-5, -5))
        .line(-0.5, 0)
        .tangentArcPoint((-2, -2))
        .close()
        .extrude(5)
        .edges()
        .fillet(1)
        .faces(">Z")
        .workplane()
        .moveTo(5, 5)
        .cskHole(4, 8, 82)
        .moveTo(15, 5)
        .cskHole(4, 8, 82)
        .moveTo(13.75, 15)
        .cskHole(4, 8, 82)
    )
    return x

def mirror():
    obj = locator()
    return obj.mirror(obj.faces(">Z"))

def instances():
    return [ "locator", "mirror" ]
