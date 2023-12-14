import cadquery as cq

def inches(inch):
    return inch * 25.4

def instance():
    return (
        cq.Workplane("XY")
        .circle(inches(2))
        .extrude(8)
    )
