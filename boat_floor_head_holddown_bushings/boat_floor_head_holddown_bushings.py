import cadquery as cq

def instance():
    return (
        cq.Workplane("XY")
        .circle(6.5)
        .extrude(1.5)
        .circle(3.7)
        .extrude(4.8)
        .circle(2.6)
        .cutThruAll()
    )
