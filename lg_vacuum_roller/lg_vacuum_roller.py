import cadquery as cq

"""
LG stick vac clunks hard over floor board joints. Three rollers under
it; the big rear one is large diameter and soft but the two front rollers
are unaccountably hard, small in diameter, and offer no cushioning.
Here's the same roller, a little wider, with both diameters oversize
to account for TPU shrinking (about 3% of the nominal 10mm OD).

WAY better feel, seems likely the floor will last longer....
"""

def instance():
    return (
        cq.Workplane("XY")
        .circle(10.5/2)
        .circle(3.5/2)
        .extrude(6)
        .edges()
        .fillet(1)
    )
