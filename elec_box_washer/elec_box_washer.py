import cadquery as cq

def inch(i):
    return i * 25.4

def washer():
    w = (
        cq.Workplane("XY")
        .circle(inch(1.70/2))
        .extrude(inch(0.125))
        .edges(">Z")
        .fillet(inch(0.08))
        .circle(inch(1.03/2))
        .cutThruAll()
    )
    return w

def instances():
    return [ "washer" ]
