"""Toilet seat anti-squirm bushing.

Make a truncated cone, 15mm across at the top, 20mm at the bottom, 10mm high
with a 7mm hole through the middle.

"""

import cadquery as cq

def instance():
    return (
        cq.Workplane("XY")
        .circle(17/2)
        .workplane(10)
        .circle(15/2)
        .loft()
        .faces(">Z")
        .circle(7/2)
        .cutThruAll()
    )
