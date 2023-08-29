import cadquery as cq

def instance():
    return (
        cq.Workplane("XY")
        .circle(41.2 / 2)
        .extrude(17)
        .faces("<Z")
        .circle(20.1 / 2)
        .cutBlind(until=13.5)
        .edges()
        .fillet(1)
    )
