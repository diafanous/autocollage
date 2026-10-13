"""Grayscale height maps and closed relief meshes. All model coordinates are mm."""
import base64
import io
import math
import struct

from PIL import Image, ImageFilter

import collage
import mounting

MAX_VERTICES = 500_000
MAX_MAP_PIXELS = 16_000_000
SPEC = dict(width_mm=(1, 5000, 100), height_mm=(1, 5000, 100),
            relief_mm=(0, 100, 10), base_mm=(0.1, 50, 2),
            spacing_mm=(0.05, 20, 0.5), gamma=(0.2, 5, 1),
            contrast=(0.1, 4, 1), smooth_mm=(0, 10, 0))


def demo_image():
    """A small local ripple image for trying the viewer without importing a file."""
    w, h = 480, 360
    im = Image.new('L', (w, h))
    pixels = []
    for y in range(h):
        for x in range(w):
            u, v = (x / (w-1) - .5)*3, (y / (h-1) - .5)*2.25
            r = math.hypot(u+.3, v-.1)
            z = .5 + .25*math.cos(10*r)*math.exp(-r*r/2) + .2*math.sin(3*u)*math.cos(3*v)
            pixels.append(round(min(1,max(0,z))*255))
    im.putdata(pixels)
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    return buf.getvalue()


def clean(raw):
    p = {}
    for key, (lo, hi, default) in SPEC.items():
        value = float(raw.get(key, default))
        if not math.isfinite(value) or not lo <= value <= hi:
            raise ValueError(f'{key} must be between {lo} and {hi}')
        p[key] = value
    p['invert'] = bool(raw.get('invert', False))
    p['source'] = raw.get('source', 'collage')
    if p['source'] not in ('collage', 'import'):
        raise ValueError('choose current collage or imported image')
    p['source_id'] = str(raw.get('source_id', ''))
    p['encoding'] = raw.get('encoding', 'binary')
    if p['encoding'] not in ('ascii', 'binary'):
        raise ValueError('STL encoding must be ascii or binary')
    p.update(mounting.clean(raw))
    return p


def grid_size(p, preview=False):
    nx = math.ceil(p['width_mm'] / p['spacing_mm']) + 1
    ny = math.ceil(p['height_mm'] / p['spacing_mm']) + 1
    if preview:
        # Keep the live viewer responsive; preserve the chosen quality in exports.
        ratio = max(1, (nx - 1) / 80, (ny - 1) / 80)
        return max(2, math.ceil((nx - 1) / ratio) + 1), max(2, math.ceil((ny - 1) / ratio) + 1)
    if nx * ny + 2 * nx + 2 * ny - 3 > MAX_VERTICES:
        raise ValueError('mesh exceeds 500,000 vertices; increase mesh spacing in mm or reduce model size')
    return nx, ny


def source_image(raw, specs, store, p, size):
    if p['source'] == 'import':
        if p['source_id'] not in store:
            raise ValueError('import an image for the luminosity map first')
        src = store[p['source_id']]
        if src.pdf:
            raise ValueError('the luminosity import must be an image')
        im = collage.raster(src)
    else:
        # Render enough pixels for the requested map, independently of print DPI.
        cp = collage.clean(raw)
        _, im = collage.compose(cp, specs, store, final=True, long_edge=max(size))
    if im.mode == 'RGBA':
        paper = Image.new('RGBA', im.size, 'white')
        im = Image.alpha_composite(paper, im)
    return im.convert('RGB').resize(size, Image.Resampling.LANCZOS)


def height_map(raw, specs, store, p, size):
    im = source_image(raw, specs, store, p, size)
    # Rec.709 weights on the source's 8-bit RGB values; white is highest by default.
    im = im.convert('L', (0.2126, 0.7152, 0.0722, 0))
    radius = p['smooth_mm'] * ((size[0] / p['width_mm'] + size[1] / p['height_mm']) / 2)
    if radius:
        im = im.filter(ImageFilter.GaussianBlur(radius))
    lut = []
    for value in range(256):
        value = min(1, max(0, (value / 255 - 0.5) * p['contrast'] + 0.5)) ** (1 / p['gamma'])
        lut.append(round(255 * (1 - value if p['invert'] else value)))
    return im.point(lut)


def mesh(raw, specs, store, options, preview=False):
    p = clean(options)
    nx, ny = grid_size(p, preview)
    im = height_map(raw, specs, store, p, (nx, ny))
    pixels = im.load()
    vertices = [(x * p['width_mm'] / (nx - 1), y * p['height_mm'] / (ny - 1),
                 p['base_mm'] + p['relief_mm'] * pixels[x, ny - 1 - y] / 255)
                for y in range(ny) for x in range(nx)]
    faces = []
    for y in range(ny - 1):
        for x in range(nx - 1):
            a = y * nx + x
            faces.extend(((a, a + 1, a + nx + 1), (a, a + nx + 1, a + nx)))
    # Counterclockwise perimeter, duplicate it at z=0, then close walls and base.
    perimeter = (list(range(nx)) + [y * nx + nx - 1 for y in range(1, ny)] +
                 [(ny - 1) * nx + x for x in range(nx - 2, -1, -1)] +
                 [y * nx for y in range(ny - 2, 0, -1)])
    start = len(vertices)
    vertices.extend((vertices[i][0], vertices[i][1], 0) for i in perimeter)
    center = len(vertices)
    vertices.append((p['width_mm'] / 2, p['height_mm'] / 2, 0))
    for k, a in enumerate(perimeter):
        j = (k + 1) % len(perimeter)
        b, c, d = perimeter[j], start + k, start + j
        faces.extend(((a, c, d), (a, d, b), (center, d, c)))
    model = dict(vertices=vertices, faces=faces, units='mm', grid=[nx, ny],
                width_mm=p['width_mm'], height_mm=p['height_mm'],
                depth_mm=p['base_mm'] + p['relief_mm'], preview=preview)
    return mounting.apply(model,p,preview)


def normal(a, b, c):
    u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
    n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    length = math.sqrt(sum(x*x for x in n)) or 1
    return tuple(x / length for x in n)


def stl(model, encoding):
    vertices, faces = model['vertices'], model['faces']
    buf = io.BytesIO()
    if encoding == 'binary':
        buf.write(b'morphaic luminosity relief; coordinates in millimeters'.ljust(80, b'\0'))
        buf.write(struct.pack('<I', len(faces)))
        for face in faces:
            a, b, c = [vertices[i] for i in face]
            buf.write(struct.pack('<12fH', *normal(a, b, c), *a, *b, *c, 0))
    else:
        buf.write(b'solid morphaic_mm\n')
        for face in faces:
            a, b, c = [vertices[i] for i in face]
            line = '  facet normal ' + ' '.join(f'{v:.9g}' for v in normal(a, b, c)) + '\n    outer loop\n'
            for vertex in (a, b, c):
                line += '      vertex ' + ' '.join(f'{v:.9g}' for v in vertex) + '\n'
            buf.write((line + '    endloop\n  endfacet\n').encode('ascii'))
        buf.write(b'endsolid morphaic_mm\n')
    return buf.getvalue()


def three_dm(model):
    import rhino3dm
    doc = rhino3dm.File3dm()
    doc.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Millimeters
    doc.Settings.ModelAbsoluteTolerance = 0.001
    for part in model.get('parts',[dict(name='morphaic luminosity relief (mm)',vertices=model['vertices'],faces=model['faces'])]):
        shape = rhino3dm.Mesh()
        for vertex in part['vertices']:
            shape.Vertices.Add(*vertex)
        for face in part['faces']:
            shape.Faces.AddFace(*face)
        shape.Normals.ComputeNormals()
        shape.Compact()
        attributes = rhino3dm.ObjectAttributes()
        attributes.Name = part['name']
        attributes.SetUserString('morphaic mounting',str(model.get('mounting',{})))
        doc.Objects.AddMesh(shape, attributes)
    return base64.b64decode(doc.Encode())


def export(raw, specs, store, options, fmt):
    if fmt not in ('stl', '3dm', 'png', 'tif'):
        raise ValueError('choose STL, 3DM, PNG or TIF for the luminosity map')
    p = clean(options)
    if fmt in ('png', 'tif'):
        dpi = collage.clean(raw)['dpi']
        size = (max(1, round(p['width_mm'] / 25.4 * dpi)), max(1, round(p['height_mm'] / 25.4 * dpi)))
        if size[0] * size[1] > MAX_MAP_PIXELS:
            raise ValueError('luminosity map exceeds 16 MP; reduce model size or DPI')
        im = height_map(raw, specs, store, p, size)
        buf = io.BytesIO()
        im.save(buf, 'PNG' if fmt == 'png' else 'TIFF', dpi=(dpi, dpi),
                **({'compression': 'tiff_deflate'} if fmt == 'tif' else {}))
        data = buf.getvalue()
    else:
        model = mesh(raw, specs, store, p)
        data = stl(model, p['encoding']) if fmt == 'stl' else three_dm(model)
    return data, f'collage-luminosity{"-mm" if fmt in ("stl", "3dm") else ""}.{fmt}'
