"""Parametric 45-degree French-cleat pair and optional rear material pocket, in mm."""
import math

SPEC = dict(cleat_height_mm=(8,100,14), cleat_depth_mm=(2,20,5),
            cleat_width=(.3,.95,.8), cleat_gap_mm=(.1,1,.3),
            pin_diameter_mm=(.5,6,1), screw_sixteenths=(1,8,3),
            hole_clearance_mm=(0,1,.3), shell_mm=(.5,5,1))


def clean(raw):
    p = {}
    for key,(lo,hi,default) in SPEC.items():
        value = float(raw.get(key,default))
        if not math.isfinite(value) or not lo <= value <= hi:
            raise ValueError(f'{key} must be between {lo} and {hi}')
        p[key] = value
    if p['screw_sixteenths'] != round(p['screw_sixteenths']):
        raise ValueError('screw diameter uses whole 1/16-inch steps')
    p['cleat'] = bool(raw.get('cleat',False))
    p['include_wall_cleat'] = bool(raw.get('include_wall_cleat',True))
    p['hollow_back'] = bool(raw.get('hollow_back',False))
    p['hardware'] = raw.get('hardware','screws')
    if p['hardware'] not in ('t-pins','plastic-pins','screws'):
        raise ValueError('choose T-pins, clear plastic pins, or screws')
    return p


def parameters(p):
    diameter = p['screw_sixteenths']*25.4/16 if p['hardware']=='screws' else p['pin_diameter_mm']
    head = diameter*1.8 if p['hardware']=='screws' else max(4,diameter*2.5)
    depth = p['cleat_depth_mm']
    height = max(p['cleat_height_mm'], depth+head+4)
    width = p['width_mm']*p['cleat_width']
    if width < 3*head+8 or height+12 > p['height_mm']:
        raise ValueError('model is too small for this cleat/hardware; enlarge it or reduce hardware size')
    if p['hollow_back'] and p['base_mm'] <= p['shell_mm']+.2:
        raise ValueError('base thickness must exceed the rear shell thickness by at least 0.2 mm')
    return dict(width=width,height=height,depth=depth,hole_diameter=diameter+p['hole_clearance_mm'],
                head_diameter=head+p['hole_clearance_mm'],margin=5)


def apply(model,p,preview=False):
    if not p['cleat']:
        return model
    import manifold3d as m
    import numpy as np
    c = parameters(p)
    width,height,depth,margin = c['width'],c['height'],c['depth'],c['margin']
    x = (p['width_mm']-width)/2
    y = p['height_mm']-margin-height
    join = min(.2,p['base_mm']/2)
    # Extrude a 2D Y/Z profile along X. Positive winding is handled by EvenOdd.
    def rail(profile):
        section=m.CrossSection([np.asarray(profile,dtype=np.float64)],m.FillRule.EvenOdd)
        return m.Manifold.extrude(section,width).transform(np.asarray([[0,0,1,0],[1,0,0,0],[0,1,0,0]],dtype=np.float64))
    relief=m.Manifold(m.Mesh(np.asarray(model['vertices'],dtype=np.float32),np.asarray(model['faces'],dtype=np.uint32)))
    if relief.is_empty():
        raise ValueError('relief mesh is not a closed solid')
    object_rail=rail([(0,join),(height,join),(height,-depth),(depth,-depth),(0,0)]).translate((x,y,0))
    spacer=m.Manifold.cube((width,4,depth+join)).translate((x,margin,-depth))
    relief=relief+object_rail+spacer
    if p['hollow_back']:
        pocket_height=y-margin-6
        if pocket_height>2 and p['width_mm']>2*margin+2:
            pocket=m.Manifold.cube((p['width_mm']-2*margin,pocket_height,p['base_mm']-p['shell_mm']+.1)).translate((margin,margin+6,-.1))
            relief=relief-pocket
    parts=[('Luminosity relief with French cleat',relief)]
    segments=16 if preview else 48
    if p['include_wall_cleat']:
        # The wall-facing side is z=-depth. Its opposing bevel supports the relief.
        gap=p['cleat_gap_mm']
        wall=rail([(0,-depth),(height-gap,-depth),(height-depth-gap,0),(0,0)])
        hole_y=(height-depth)/2
        for hole_x in (width*.25,width*.75):
            shaft=m.Manifold.cylinder(depth+.4,c['hole_diameter']/2,circular_segments=segments).translate((hole_x,hole_y,-depth-.2))
            if p['hardware']=='screws':
                seat_depth=min(depth*.65,(c['head_diameter']-c['hole_diameter'])/2)
                seat=m.Manifold.cylinder(seat_depth+.05,c['hole_diameter']/2,c['head_diameter']/2,segments).translate((hole_x,hole_y,-seat_depth))
            elif p['hardware']=='t-pins':
                seat=m.Manifold.cube((c['head_diameter']*1.5,c['hole_diameter']+1,min(1,depth/3)+.1)).translate((hole_x-c['head_diameter']*.75,hole_y-(c['hole_diameter']+1)/2,-min(1,depth/3)))
            else:
                seat=m.Manifold.cylinder(min(1,depth/3)+.1,c['head_diameter']/2,circular_segments=segments).translate((hole_x,hole_y,-min(1,depth/3)))
            wall=wall-shaft-seat
        # Place the matching part beside the relief for printing/export; no fused solids.
        wall=wall.translate((p['width_mm']+8,margin,0))
        parts.append(('Matching wall cleat - '+p['hardware'],wall))
    vertices,faces,objects=[],[],[]
    for name,solid in parts:
        mesh=solid.to_mesh()
        if solid.is_empty() or solid.status()!=m.Error.NoError:
            raise ValueError('mounting geometry could not form a closed solid; adjust dimensions')
        part_vertices=mesh.vert_properties[:,:3].tolist()
        part_faces=mesh.tri_verts.tolist()
        objects.append(dict(name=name,vertices=part_vertices,faces=part_faces))
        offset=len(vertices)
        vertices.extend(part_vertices)
        faces.extend(tuple(i+offset for i in face) for face in part_faces)
    model.update(vertices=vertices,faces=faces,parts=objects,
                 mounting=dict(bevel_degrees=45,hardware=p['hardware'],clearance_mm=p['cleat_gap_mm'],
                               rail_height_mm=height,rail_depth_mm=depth,hole_diameter_mm=c['hole_diameter'],
                               assembly_wall_offset_y_mm=y-(height-depth),
                               wall_cleat_separate=p['include_wall_cleat'],hollow_back=p['hollow_back']))
    model['bounds']=[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]]
    return model
