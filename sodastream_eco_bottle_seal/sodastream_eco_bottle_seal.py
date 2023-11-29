import cadquery as cq

"""
Seal inside sodastream bottle cap, for TPU. Not perfect: probably
needs to be printed on a smooth plate to get a good sealing surface,
and I didn't account enough for TPU shrinkage on cooling (about 3%
measured on another project) - it was hard to jam this into place.
"""

def instance():
    return (
        cq.Workplane("XY")
        .circle(34/2)
        .circle(23/2)
        .extrude(2.5)
    )
