"""
CQ model of a half-roller to support the front part of IC dollies onto and
off of the road trailer.
"""

import os
import math
import cadquery as cq

def mm(mm: float) -> float:
    return mm

def inches(mm: float) -> float:
    return mm * 25.4

PARAMS = {
    'axle radius': inches(0.5),
    'radial clearance': mm(0.0),  # try 0.3 but first prototype didn't include this
    'axial clearance': mm(1),
    'wall thickness': mm(2.5),
    'full width': inches(4.0),
    'full flat width': inches(3.0),  # matching the width of the road trailer central rail
    'max radius': inches(1.5),
    'flange flat': mm(3),
    'roller bearing diameter': inches(0.25),
    'spacer flange radial': mm(3),
    'flanges axial': mm(3),
    'interference overlap': mm(8),
}


                       
def dolly_roller(p=PARAMS):
    cylinder_inner_radius = p['axle radius'] + p['roller bearing diameter'] + p['radial clearance']
    cylinder_outer_radius = cylinder_inner_radius + p['wall thickness']
    roller_Z = p['full width'] / 2  # we'll trim for central gap later
    angled_face_Z = roller_Z - p['full flat width'] / 2 - p['flange flat']
    angled_face_X = p['max radius'] - cylinder_outer_radius

    solid = (cq.Workplane("XZ")
             .line(0, roller_Z)  # current workplane's Y
             .line(cylinder_outer_radius, 0)
             .line(0, -(p['full flat width'] / 2))
             .line(angled_face_X, -angled_face_Z)
             .line(0, -(p['flange flat']))
             .close()
             .revolve(360)
             .faces("<Z")
             .workplane()
             .circle(cylinder_inner_radius)
             .cutThruAll())
    return solid

def spacer(p=PARAMS):
    cylinder_inner_radius = p['axle radius'] + p['radial clearance']
    cylinder_outer_radius = cylinder_inner_radius + p['wall thickness']
    length = p['length overall'] - p['full width'] - p['flanges axial'] * 4 - p['axial clearance']
    solid = (cq.Workplane("XY")
             .circle(cylinder_outer_radius + p['spacer flange radial'])
             .extrude(p['flanges axial'])
             .faces("<Z")
             .circle(cylinder_outer_radius)
             .extrude(p['length overall'] / 2 - p['flanges axial'] - p['axial clearance'])
             .circle(cylinder_inner_radius)
             .cutThruAll())
    return solid

def cap(p=PARAMS):
    cylinder_inner_radius = p['axle radius'] + p['radial clearance']
    interference_outer_radius = p['axle radius'] + p['roller bearing diameter'] + p['radial clearance']
    surface_outer_radius = interference_outer_radius + p['wall thickness']
    solid = (cq.Workplane("XY")
             .circle(surface_outer_radius)
             .extrude(p['flanges axial'])
             .circle(interference_outer_radius)
             .extrude(p['interference overlap'])
             .circle(cylinder_inner_radius)
             .cutThruAll())
    return solid

def instance():
    PARAMS['length overall'] = os.environ.get('LENGTH_OVERALL_MM', inches(12))
    PARAMS['central support gap'] = os.environ.get('CENTRAL_SUPPORT_GAP_MM', 0)

    select = os.environ.get('SELECT', 'dolly_roller')
    print(f'select:{select} len:{PARAMS["length overall"]} gap:{PARAMS["central support gap"]}')
    if select == 'dolly_roller':
        return dolly_roller()
    elif select == 'cap':
        return cap()
    elif select == 'cage':
        return cage()
    elif select == 'spacer':
        return spacer()
    else:
        # agglomerate into one .stl
        raise RuntimeError("implement agglomeration")
