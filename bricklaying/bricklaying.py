import types
import math
import cadquery as cq
import cqmodel.util

def mm(x):
    return x

def degrees(x):
    return x

def inches(x):
    return x * 25.4

def instance():
    return (
        cq.Workplane("XY")
        .lineTo(inches(0.0), inches(2.0))
        .lineTo(inches(0.5), inches(2))
        .lineTo(inches(0.5), inches(0.5))
        .lineTo(inches(1.5), inches(0.5))
        .lineTo(inches(1.5), inches(0.0))
        .close()
        .extrude(inches(1.0))
        .moveTo(inches(0.5), inches(0.5))
        .circle(inches(0.125))
        .cutThruAll()
        .faces(">>Y")
        .workplane(invert=True)
        .moveTo(-inches(0.5), -inches(0.5))
        .circle(inches(0.03125))
        .cutThruAll()
        .faces(">>X[-2]")
        .workplane()
        .moveTo(-inches(0.85), inches(0.5))
        .circle(inches(0.03125))
        .extrude(inches(0.03125))
    )
