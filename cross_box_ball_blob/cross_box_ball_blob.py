import cadquery as cq

shape = cq.Workplane("XY").box(1,3,0.5)
shape  = shape.workplane().box(3,1,0.5)
shape  = shape.workplane().sphere(0.6)
shape  = shape.edges().fillet(0.125)
