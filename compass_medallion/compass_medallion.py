import os.path
import cadquery as cq

def inch(i):
    return i * 25.4

def medallion():
    p = os.path.join("compass_medallion", "traced1.dxf")
    obj = (
        cq.Workplane("XY")
        .circle(inch(4.5/2))
        .extrude(10)
        .circle(inch(3.5/2))
        .cutBlind(5)
        .edges()
        .fillet(1)
        .cut(cq.importers.importDXF(p).wires().toPending().extrude(1))
        .faces("<Z")
        .workplane()
        .rect(inch(2.83), inch(2.83), forConstruction=True)
        .vertices()
        .cskHole(4, 8, 82)
    )
    return obj

def instances():
    return [ "medallion" ]
