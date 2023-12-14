import cadquery as cq

def instance(nubs_horizontal=20):
    rect = ( 16 * nubs_horizontal, 25)
    inst = (
        cq.Workplane("XY")
        .rect(*rect)
        .extrude(4)
        .edges("|Z")
        .fillet(5)

        .edges(">Z")
        .fillet(3)

        .pushPoints([(  x * 16 + 8 , -8 if x % 2 else  8) for x in range(0, nubs_horizontal//2)])
        .circle(2)
        .pushPoints([(-(x * 16 + 8),  8 if x % 2 else -8) for x in range(0, nubs_horizontal//2)])
        .circle(2)
        .extrude(10)
        .edges("not <Z")
        .fillet(1.5)

        .faces("<Z[-2]")
        .workplane()
        .pushPoints([(-16 * 8, 0), (0,0), (16 * 8, 0)])
        .cskHole(5, 8, 82)
    )

    return inst
