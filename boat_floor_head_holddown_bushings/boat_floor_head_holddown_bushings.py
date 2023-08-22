import cadquery as cq

def bush():
    bush = (
        cq.Workplane("XY")
        .circle(6.5)
        .extrude(1.5)
        .circle(3.7)
        .extrude(4.8)
        .circle(2.6)
        .cutThruAll()
    )
    return bush

def instances():
    return [ "bush" ]
