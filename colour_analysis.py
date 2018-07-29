from __future__ import division

import json
import numpy as np
import os
import re
from werkzeug.contrib.cache import SimpleCache

from colour import RGB_COLOURSPACES, RGB_to_XYZ, read_image
from colour.models import (XYZ_to_colourspace_model, XYZ_to_RGB, RGB_to_RGB,
                           oetf_reverse_sRGB)
from colour.plotting import (COLOUR_STYLE_CONSTANTS, filter_cmfs,
                             filter_RGB_colourspaces)
from colour.utilities import first_item, normalise_maximum, tsplit, tstack

LINEAR_FILE_FORMATS = ('.exr', '.hdr')

DEFAULT_FLOAT_DTYPE = np.float16

COLOURSPACE_MODELS = ('CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS',
                      'CIE UVW', 'IPT', 'Hunter Lab', 'Hunter Rdab')

COLOURSPACE_MODELS_LABELS = {
    'CIE XYZ': ('X', 'Y', 'Z'),
    'CIE xyY': ('x', 'Y', 'y'),
    'CIE Lab': ('a*', 'L*', 'b*'),
    'CIE Luv': ('u*', 'L*', 'v*'),
    'CIE UCS': ('U', 'W', 'V'),
    'CIE UVW': ('U*', 'W*', 'V*'),
    'IPT': ('P', 'I', 'T'),
    'Hunter Lab': ('a', 'L', 'b'),
    'Hunter Rdab': ('a', 'Rd', 'b')
}

PRIMARY_COLOURSPACE = 'sRGB'

SECONDARY_COLOURSPACE = 'DCI-P3'

IMAGE_COLOURSPACE = 'Primary'

COLOURSPACE_MODEL = 'CIE xyY'

IMAGE_CACHE = SimpleCache(default_timeout=1440)


def load_image(path):
    RGB = IMAGE_CACHE.get(path)
    if RGB is None:
        RGB = read_image(path)
        if os.path.splitext(path)[-1].lower() not in LINEAR_FILE_FORMATS:
            RGB = oetf_reverse_sRGB(RGB)
        IMAGE_CACHE.set(path, RGB)

    return RGB


def colourspace_model_axis_reorder(a, model=None):
    i, j, k = tsplit(a)
    if model in ('CIE XYZ', ):
        a = tstack((k, j, i))
    elif model in ('CIE UCS', 'CIE UVW', 'CIE xyY'):
        a = tstack((j, k, i))
    elif model in ('CIE Lab', 'CIE LCHab', 'CIE Luv', 'CIE LCHuv', 'IPT',
                   'Hunter Lab', 'Hunter Rdab'):
        a = tstack((k, i, j))

    return a


def colourspace_model_faces_reorder(a, model=None):
    if model in ('CIE XYZ', ):
        a = a[::-1]

    return a


def colourspace_models():
    return json.dumps(COLOURSPACE_MODELS_LABELS)


def RGB_colourspaces():
    return json.dumps(RGB_COLOURSPACES.keys())


def buffer_geometry(**kwargs):
    data = {
        'metadata': {
            'version': 4,
            'type': 'BufferGeometry',
            'generator': 'colour-three'
        },
        'data': {
            'attributes': {}
        }
    }

    data_types_conversion = {
        'float16': 'Float32Array',  # Unsupported, casted up.
        'float32': 'Float32Array',
        'float64': 'Float32Array',  # Unsupported, casted down.
        'uint16': 'Uint16Array',
        'uint32': 'Uint32Array',
        'uint64': 'Uint32Array',  # Unsupported, casted down.
    }

    for attribute, values in kwargs.items():
        values = np.asarray(values)
        shape = values.shape
        dtype = values.dtype

        values = np.ravel(values)

        if 'float' in dtype.name:
            values = np.around(values, np.finfo(DEFAULT_FLOAT_DTYPE).precision)

        data['data']['attributes'][attribute] = {
            'itemSize': shape[-1],
            'type': data_types_conversion[dtype.name],
            'array': values.tolist()
        }

    return json.dumps(data)


def create_plane(width=1,
                 height=1,
                 width_segments=1,
                 height_segments=1,
                 direction='+z'):
    """
    Generates vertices & indices for a filled and outlined plane.

    Parameters
    ----------
    width : float
        Plane width.
    height : float
        Plane height.
    width_segments : int
        Plane segments count along the width.
    height_segments : float
        Plane segments count along the height.
    direction: unicode
        ``{'-x', '+x', '-y', '+y', '-z', '+z'}``
        Direction the plane will be facing.

    Returns
    -------
    vertices : array
        Array of vertices suitable for use as a VertexBuffer.
    faces : array
        Indices to use to produce a filled plane.
    outline : array
        Indices to use to produce an outline of the plane.

    References
    ----------
    .. [1] Cabello, R. (n.d.). PlaneBufferGeometry.js. Retrieved May 12, 2015,
        from http://git.io/vU1Fh
    """

    x_grid = width_segments
    y_grid = height_segments

    x_grid1 = x_grid + 1
    y_grid1 = y_grid + 1

    # Positions, normals and texcoords.
    positions = np.zeros(x_grid1 * y_grid1 * 3)
    normals = np.zeros(x_grid1 * y_grid1 * 3)
    texcoords = np.zeros(x_grid1 * y_grid1 * 2)

    y = np.arange(y_grid1) * height / y_grid - height / 2
    x = np.arange(x_grid1) * width / x_grid - width / 2

    positions[::3] = np.tile(x, y_grid1)
    positions[1::3] = -np.repeat(y, x_grid1)

    normals[2::3] = 1

    texcoords[::2] = np.tile(np.arange(x_grid1) / x_grid, y_grid1)
    texcoords[1::2] = np.repeat(1 - np.arange(y_grid1) / y_grid, x_grid1)

    # Faces and outline.
    faces, outline = [], []
    for i_y in range(y_grid):
        for i_x in range(x_grid):
            a = i_x + x_grid1 * i_y
            b = i_x + x_grid1 * (i_y + 1)
            c = (i_x + 1) + x_grid1 * (i_y + 1)
            d = (i_x + 1) + x_grid1 * i_y

            faces.extend(((a, b, d), (b, c, d)))
            outline.extend(((a, b), (b, c), (c, d), (d, a)))

    positions = np.reshape(positions, (-1, 3))
    texcoords = np.reshape(texcoords, (-1, 2))
    normals = np.reshape(normals, (-1, 3))

    faces = np.reshape(faces, (-1, 3)).astype(np.uint32)
    outline = np.reshape(outline, (-1, 2)).astype(np.uint32)

    direction = direction.lower()
    if direction in ('-x', '+x'):
        shift, neutral_axis = 1, 0
    elif direction in ('-y', '+y'):
        shift, neutral_axis = -1, 1
    elif direction in ('-z', '+z'):
        shift, neutral_axis = 0, 2

    sign = -1 if '-' in direction else 1

    positions = np.roll(positions, shift, -1)
    normals = np.roll(normals, shift, -1) * sign
    colors = np.ravel(positions)
    colors = np.hstack((np.reshape(
        np.interp(colors, (np.min(colors), np.max(colors)), (0, 1)),
        positions.shape), np.ones((positions.shape[0], 1))))
    colors[..., neutral_axis] = 0

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3),
                         ('texcoord', np.float32, 2),
                         ('normal', np.float32, 3), ('colour', np.float32, 4)])

    vertices['position'] = positions
    vertices['texcoord'] = texcoords
    vertices['normal'] = normals
    vertices['colour'] = colors

    return vertices, faces, outline


def create_box(width=1,
               height=1,
               depth=1,
               width_segments=1,
               height_segments=1,
               depth_segments=1,
               planes=None):
    """
    Generates vertices & indices for a filled and outlined box.

    Parameters
    ----------
    width : float
        Box width.
    height : float
        Box height.
    depth : float
        Box depth.
    width_segments : int
        Box segments count along the width.
    height_segments : float
        Box segments count along the height.
    depth_segments : float
        Box segments count along the depth.
    planes: array_like
        Any combination of ``{'-x', '+x', '-y', '+y', '-z', '+z'}``
        Included planes in the box construction.

    Returns
    -------
    vertices : array
        Array of vertices suitable for use as a VertexBuffer.
    faces : array
        Indices to use to produce a filled box.
    outline : array
        Indices to use to produce an outline of the box.
    """

    planes = (('+x', '-x', '+y', '-y', '+z', '-z')
              if planes is None else [d.lower() for d in planes])

    w_s, h_s, d_s = width_segments, height_segments, depth_segments

    planes_m = []
    if '-z' in planes:
        planes_m.append(list(create_plane(width, depth, w_s, d_s, '-z')))
        planes_m[-1][0]['position'][..., 2] -= height / 2
        planes_m[-1][1] = np.fliplr(planes_m[-1][1])
    if '+z' in planes:
        planes_m.append(list(create_plane(width, depth, w_s, d_s, '+z')))
        planes_m[-1][0]['position'][..., 2] += height / 2

    if '-y' in planes:
        planes_m.append(list(create_plane(height, width, h_s, w_s, '-y')))
        planes_m[-1][0]['position'][..., 1] -= depth / 2
        planes_m[-1][1] = np.fliplr(planes_m[-1][1])
    if '+y' in planes:
        planes_m.append(list(create_plane(height, width, h_s, w_s, '+y')))
        planes_m[-1][0]['position'][..., 1] += depth / 2

    if '-x' in planes:
        planes_m.append(list(create_plane(depth, height, d_s, h_s, '-x')))
        planes_m[-1][0]['position'][..., 0] -= width / 2
        planes_m[-1][1] = np.fliplr(planes_m[-1][1])
    if '+x' in planes:
        planes_m.append(list(create_plane(depth, height, d_s, h_s, '+x')))
        planes_m[-1][0]['position'][..., 0] += width / 2

    positions = np.zeros((0, 3), dtype=np.float32)
    texcoords = np.zeros((0, 2), dtype=np.float32)
    normals = np.zeros((0, 3), dtype=np.float32)

    faces = np.zeros((0, 3), dtype=np.uint32)
    outline = np.zeros((0, 2), dtype=np.uint32)

    offset = 0
    for vertices_p, faces_p, outline_p in planes_m:
        positions = np.vstack((positions, vertices_p['position']))
        texcoords = np.vstack((texcoords, vertices_p['texcoord']))
        normals = np.vstack((normals, vertices_p['normal']))

        faces = np.vstack((faces, faces_p + offset))
        outline = np.vstack((outline, outline_p + offset))
        offset += vertices_p['position'].shape[0]

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3),
                         ('texcoord', np.float32, 2),
                         ('normal', np.float32, 3), ('colour', np.float32, 4)])

    colors = np.ravel(positions)
    colors = np.hstack((np.reshape(
        np.interp(colors, (np.min(colors), np.max(colors)), (0, 1)),
        positions.shape), np.ones((positions.shape[0], 1))))

    vertices['position'] = positions
    vertices['texcoord'] = texcoords
    vertices['normal'] = normals
    vertices['colour'] = colors

    return vertices, faces, outline


def RGB_colourspace_volume_visual(colourspace=PRIMARY_COLOURSPACE,
                                  colourspace_model=COLOURSPACE_MODEL,
                                  segments=16,
                                  uniform_colour=None,
                                  wireframe=False,
                                  wireframe_colour=None):
    colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(re.escape(colourspace))))

    cube = create_box(
        width_segments=segments,
        height_segments=segments,
        depth_segments=segments)

    vertices = cube[0]['position'] + 0.5
    faces = colourspace_model_faces_reorder(
        np.reshape(cube[1], (-1, 1)), colourspace_model)
    # outline = cube[2]
    RGB = cube[0]['colour'] if uniform_colour is None else uniform_colour

    XYZ = RGB_to_XYZ(vertices, colourspace.whitepoint, colourspace.whitepoint,
                     colourspace.RGB_to_XYZ_matrix)
    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 colourspace_model), colourspace_model)
    vertices[np.isnan(vertices)] = 0

    # if wireframe:
    #     vertices = vertices[outline].reshape(-1, 3)
    #                if wireframe_colour is None else wireframe_colour)

    #     mask = np.full(
    #         outline.shape[0], face_mask(face_vertex_colours=True)).reshape(
    #             -1, 1)

    #     return geometry(
    #         name=colourspace.name, vertices=vertices, colours=RGB,
    #         faces=np.hstack([mask, outline, outline]))
    # else:

    # mask = np.full(
    #     faces.shape[0], face_mask(face_vertex_colours=True)).reshape(-1, 1)

    return buffer_geometry(position=vertices, color=RGB, index=faces)


def spectral_locus_visual(colourspace=PRIMARY_COLOURSPACE,
                          colourspace_model=COLOURSPACE_MODEL,
                          cmfs='CIE 1931 2 Degree Standard Observer',
                          uniform_colour=None):

    colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(re.escape(colourspace))))

    cmfs = first_item(filter_cmfs(cmfs))
    XYZ = cmfs.values

    XYZ = np.vstack((XYZ, XYZ[0, ...]))

    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 colourspace_model), colourspace_model)
    vertices[np.isnan(vertices)] = 0

    RGB = normalise_maximum(
        XYZ_to_RGB(XYZ, colourspace.whitepoint, colourspace.whitepoint,
                   colourspace.XYZ_to_RGB_matrix),
        axis=-1) if uniform_colour is None else uniform_colour

    return buffer_geometry(position=vertices, color=RGB)


def RGB_image_scatter_visual(path,
                             primary_colourspace=PRIMARY_COLOURSPACE,
                             secondary_colourspace=SECONDARY_COLOURSPACE,
                             image_colourspace=IMAGE_COLOURSPACE,
                             colourspace_model=COLOURSPACE_MODEL,
                             uniform_colour=None,
                             sub_sampling=25,
                             out_of_primary_colourspace_gamut=False,
                             out_of_secondary_colourspace_gamut=False,
                             saturate=False):
    primary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(primary_colourspace))))
    secondary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(secondary_colourspace))))

    colourspace = (primary_colourspace if image_colourspace == 'Primary' else
                   secondary_colourspace)

    RGB = load_image(path)

    if saturate:
        RGB = np.clip(RGB, 0, 1)

    RGB = RGB[..., 0:3].reshape(-1, 3)[::sub_sampling]

    XYZ = RGB_to_XYZ(RGB, colourspace.whitepoint, colourspace.whitepoint,
                     colourspace.RGB_to_XYZ_matrix)
    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 colourspace_model), colourspace_model)
    vertices[np.isnan(vertices)] = 0

    RGB = RGB if uniform_colour is None else uniform_colour

    return buffer_geometry(position=vertices, color=RGB)


def image_data(path,
               primary_colourspace=PRIMARY_COLOURSPACE,
               secondary_colourspace=SECONDARY_COLOURSPACE,
               image_colourspace=IMAGE_COLOURSPACE,
               out_of_primary_colourspace_gamut=False,
               out_of_secondary_colourspace_gamut=False,
               saturate=False):
    primary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(primary_colourspace))))
    secondary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(secondary_colourspace))))

    colourspace = (primary_colourspace if image_colourspace == 'Primary' else
                   secondary_colourspace)

    RGB = load_image(path)

    if saturate:
        RGB = np.clip(RGB, 0, 1)

    if out_of_primary_colourspace_gamut:
        if image_colourspace == 'Secondary':
            RGB = RGB_to_RGB(RGB, secondary_colourspace, primary_colourspace)

        RGB[RGB >= 0] = 0
        RGB[RGB < 0] = 1

    if out_of_secondary_colourspace_gamut:
        if image_colourspace == 'Primary':
            RGB = RGB_to_RGB(RGB, primary_colourspace, secondary_colourspace)

        RGB[RGB >= 0] = 0
        RGB[RGB < 0] = 1

    shape = RGB.shape
    RGB = np.ravel(RGB[..., 0:3].reshape(-1, 3))
    RGB = np.around(RGB, np.finfo(DEFAULT_FLOAT_DTYPE).precision)

    return json.dumps({
        'width': shape[1],
        'height': shape[0],
        'data': RGB.tolist()
    })
