# -*- coding: utf-8 -*-
"""
Colour - Analysis
=================

Defines various objects that typically output the geometry as JSON to be
loaded by "Three.js".
"""

from __future__ import division

import json
import numpy as np
import os
import re
from collections import OrderedDict
from werkzeug.contrib.cache import SimpleCache

from colour import (LOG_DECODING_CURVES, OETFS_REVERSE,
                    RGB_COLOURSPACES, RGB_to_RGB, RGB_to_XYZ, XYZ_to_RGB,
                    read_image)
from colour.models import XYZ_to_colourspace_model, function_gamma
from colour.plotting import filter_cmfs, filter_RGB_colourspaces
from colour.utilities import first_item, normalise_maximum, tsplit, tstack

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2018 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = [
    'LINEAR_FILE_FORMATS', 'DEFAULT_FLOAT_DTYPE', 'COLOURSPACE_MODELS',
    'COLOURSPACE_MODELS_LABELS', 'DECODING_CCTFS', 'PRIMARY_COLOURSPACE',
    'SECONDARY_COLOURSPACE', 'IMAGE_COLOURSPACE', 'IMAGE_DECODING_CCTF',
    'COLOURSPACE_MODEL', 'IMAGE_CACHE', 'load_image',
    'colourspace_model_axis_reorder', 'colourspace_model_faces_reorder',
    'decoding_cctfs', 'colourspace_models', 'RGB_colourspaces',
    'buffer_geometry', 'create_plane', 'create_box',
    'RGB_colourspace_volume_visual', 'spectral_locus_visual',
    'RGB_image_scatter_visual', 'image_data'
]

LINEAR_FILE_FORMATS = ('.exr', '.hdr')
"""
Assumed linear image formats.

LINEAR_IMAGE_FORMATS : tuple
"""

DEFAULT_FLOAT_DTYPE = np.float16
"""
Default floating point number dtype. Float16 is chosen over Float32 because it
is lighter and thus more adapted to send data from the server to client.

DEFAULT_FLOAT_DTYPE : type
"""

COLOURSPACE_MODELS = ('CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS',
                      'CIE UVW', 'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'IPT',
                      'JzAzBz', 'OSA UCS', 'hdr-CIELAB', 'hdr-IPT')
"""
Reference colourspace models defining available colour transformations from
CIE XYZ tristimulus values.

COLOURSPACE_MODELS : tuple
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'IPT', 'JzAzBz', 'OSA UCS',
    'hdr-CIELAB', 'hdr-IPT'}**
"""

COLOURSPACE_MODELS_LABELS = {
    'CIE XYZ': ('X', 'Y', 'Z'),
    'CIE xyY': ('x', 'Y', 'y'),
    'CIE Lab': ('a*', 'L*', 'b*'),
    'CIE Luv': ('u*', 'L*', 'v*'),
    'CIE UCS': ('U', 'W', 'V'),
    'CIE UVW': ('U*', 'W*', 'V*'),
    'DIN 99': ('a99', 'L99', 'b99'),
    'Hunter Lab': ('a', 'L', 'b'),
    'Hunter Rdab': ('a', 'Rd', 'b'),
    'IPT': ('P', 'I', 'T'),
    'JzAzBz': ('Az', 'Jz', 'Bz'),
    'OSA UCS': ('j', 'J', 'g'),
    'hdr-CIELAB': ('a hdr', 'L hdr', 'b hdr'),
    'hdr-IPT': ('P hdr', 'I hdr', 'T hdr')
}
"""
Reference colourspace models axes labels, ordered so that luminance is on *Y*
axis.

COLOURSPACE_MODELS : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'IPT', 'JzAzBz', 'OSA UCS',
    'hdr-CIELAB', 'hdr-IPT'}**
"""

DECODING_CCTFS = OrderedDict()
DECODING_CCTFS.update(
    sorted({
        'Gamma 2.2': lambda x: function_gamma(x, 2.2),
        'Gamma 2.4': lambda x: function_gamma(x, 2.4),
        'Gamma 2.6': lambda x: function_gamma(x, 2.6)
    }.items()))
DECODING_CCTFS.update(sorted(OETFS_REVERSE.items()))
DECODING_CCTFS.update(sorted(LOG_DECODING_CURVES.items()))
"""
Decoding colour component transfer functions.

DECODING_CCTFS : OrderedDict
"""

PRIMARY_COLOURSPACE = 'sRGB'
"""
Primary analysis RGB colourspace.

PRIMARY_COLOURSPACE : unicode
"""

SECONDARY_COLOURSPACE = 'DCI-P3'
"""
Secondary analysis RGB colourspace.

SECONDARY_COLOURSPACE : unicode
"""

IMAGE_COLOURSPACE = 'Primary'
"""
Analysed image RGB colourspace either *Primary* or *Secondary*.

IMAGE_COLOURSPACE : unicode
"""

IMAGE_DECODING_CCTF = 'sRGB'
"""
Analysed image RGB colourspace decoding colour component transfer function.

IMAGE_DECODING_CCTF : unicode
"""

COLOURSPACE_MODEL = 'CIE xyY'
"""
Analysis colour model.

COLOURSPACE_MODEL : unicode
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'IPT', 'JzAzBz', 'OSA UCS',
    'hdr-CIELAB', 'hdr-IPT'}**
"""

IMAGE_CACHE = SimpleCache(default_timeout=60 * 24 * 7)
"""
Server side cache for images.

IMAGE_CACHE : SimpleCache
"""


def load_image(path, decoding_cctf='sRGB'):
    """
    Loads the image at given path and caches it in `IMAGE_CACHE` cache. If the
    image is already cached, it is returned directly.

    Parameters
    ----------
    path : unicode
        Image path.
    decoding_cctf : unicode, optional
        Decoding colour component transfer function (Decoding CCTF) /
        electro-optical transfer function (EOTF / EOCF) that maps an
        :math:`R'G'B'` video component signal value to tristimulus values at
        the display.

    Returns
    -------
    ndarray
        Image as a ndarray.
    """

    key = '{0}-{1}'.format(path, decoding_cctf)

    RGB = IMAGE_CACHE.get(key)
    if RGB is None:
        RGB = read_image(path)

        if os.path.splitext(path)[-1].lower() not in LINEAR_FILE_FORMATS:
            RGB = DECODING_CCTFS[decoding_cctf](RGB)

        IMAGE_CACHE.set(key, RGB)

    return RGB


def colourspace_model_axis_reorder(a, model=None):
    """
    Reorder the axes of given colourspace model :math:`a` array so that
    luminance is on *Y* axis.

    Parameters
    ----------
    a : array_like
        Colourspace model :math:`a` array.
    model : unicode, optional
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'IPT', 'JzAzBz', 'OSA UCS',
        'hdr-CIELAB', 'hdr-IPT'}**
        Colourspace model.

    Returns
    -------
    ndarray
        Reordered colourspace model :math:`a` array.
    """

    i, j, k = tsplit(a)
    if model in ('CIE XYZ', ):
        a = tstack((k, j, i))
    elif model in ('CIE UCS', 'CIE UVW', 'CIE xyY'):
        a = tstack((j, k, i))
    elif model in ('CIE Lab', 'CIE LCHab', 'CIE Luv', 'CIE LCHuv', 'DIN 99',
                   'Hunter Lab', 'Hunter Rdab', 'IPT', 'JzAzBz', 'OSA UCS',
                   'hdr-CIELAB', 'hdr-IPT'):
        a = tstack((k, i, j))

    return a


def colourspace_model_faces_reorder(a, model=None):
    """
    Reorder the faces of given colourspace model :math:`a` array.

    Parameters
    ----------
    a : array_like
        Colourspace model :math:`a` array.
    model : unicode, optional
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'IPT', 'JzAzBz', 'OSA UCS',
        'hdr-CIELAB', 'hdr-IPT'}**
        Colourspace model.

    Returns
    -------
    Figure
        Reordered colourspace model :math:`a` array.
    """

    if model in ('CIE XYZ', ):
        a = a[::-1]

    return a


def decoding_cctfs():
    """
    Returns the decoding colour component transfer functions formatted as
    *JSON*.

    Returns
    -------
    unicode
        Decoding colour component transfer functions formatted as *JSON*.
    """

    return json.dumps(DECODING_CCTFS.keys())


def colourspace_models():
    """
    Returns the colourspace models formatted as *JSON*.

    Returns
    -------
    unicode
        Colourspace models formatted as *JSON*.
    """

    return json.dumps(COLOURSPACE_MODELS_LABELS)


def RGB_colourspaces():
    """
    Returns the RGB colourspaces formatted as *JSON*.

    Returns
    -------
    unicode
        RGB colourspaces formatted as *JSON*.
    """

    return json.dumps(RGB_COLOURSPACES.keys())


def buffer_geometry(**kwargs):
    """
    Returns given geometry formatted as *JSON* compatible with *Three.js*
    `BufferGeometryLoader <https://threejs.org/docs/#api/loaders/\
BufferGeometryLoader>`_.

    Other Parameters
    ----------------
    \**kwargs : dict, optional
        Valid attributes from `BufferGeometryLoader <https://threejs.org/docs/\
#api/loaders/BufferGeometryLoader>`_.

    Returns
    -------
    unicode
        Geometry formatted as *JSON*.
    """

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
            values = np.nan_to_num(
                np.around(values,
                          np.finfo(DEFAULT_FLOAT_DTYPE).precision))

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
    Generates vertices and indices for a filled and outlined plane.

    Parameters
    ----------
    width : float, optional
        Plane width.
    height : float, optional
        Plane height.
    width_segments : int, optional
        Plane segments count along the width.
    height_segments : float, optional
        Plane segments count along the height.
    direction: unicode, optional
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

    # Positions, normals and uvs.
    positions = np.zeros(x_grid1 * y_grid1 * 3)
    normals = np.zeros(x_grid1 * y_grid1 * 3)
    uvs = np.zeros(x_grid1 * y_grid1 * 2)

    y = np.arange(y_grid1) * height / y_grid - height / 2
    x = np.arange(x_grid1) * width / x_grid - width / 2

    positions[::3] = np.tile(x, y_grid1)
    positions[1::3] = -np.repeat(y, x_grid1)

    normals[2::3] = 1

    uvs[::2] = np.tile(np.arange(x_grid1) / x_grid, y_grid1)
    uvs[1::2] = np.repeat(1 - np.arange(y_grid1) / y_grid, x_grid1)

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
    uvs = np.reshape(uvs, (-1, 2))
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
                        [('position', np.float32, 3), ('uv', np.float32, 2),
                         ('normal', np.float32, 3), ('colour', np.float32, 4)])

    vertices['position'] = positions
    vertices['uv'] = uvs
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
    Generates vertices and indices for a filled and outlined box.

    Parameters
    ----------
    width : float, optional
        Box width.
    height : float, optional
        Box height.
    depth : float, optional
        Box depth.
    width_segments : int, optional
        Box segments count along the width.
    height_segments : float, optional
        Box segments count along the height.
    depth_segments : float, optional
        Box segments count along the depth.
    planes: array_like, optional
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
    uvs = np.zeros((0, 2), dtype=np.float32)
    normals = np.zeros((0, 3), dtype=np.float32)

    faces = np.zeros((0, 3), dtype=np.uint32)
    outline = np.zeros((0, 2), dtype=np.uint32)

    offset = 0
    for vertices_p, faces_p, outline_p in planes_m:
        positions = np.vstack((positions, vertices_p['position']))
        uvs = np.vstack((uvs, vertices_p['uv']))
        normals = np.vstack((normals, vertices_p['normal']))

        faces = np.vstack((faces, faces_p + offset))
        outline = np.vstack((outline, outline_p + offset))
        offset += vertices_p['position'].shape[0]

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3), ('uv', np.float32, 2),
                         ('normal', np.float32, 3), ('colour', np.float32, 4)])

    colors = np.ravel(positions)
    colors = np.hstack((np.reshape(
        np.interp(colors, (np.min(colors), np.max(colors)), (0, 1)),
        positions.shape), np.ones((positions.shape[0], 1))))

    vertices['position'] = positions
    vertices['uv'] = uvs
    vertices['normal'] = normals
    vertices['colour'] = colors

    return vertices, faces, outline


def RGB_colourspace_volume_visual(colourspace=PRIMARY_COLOURSPACE,
                                  colourspace_model=COLOURSPACE_MODEL,
                                  segments=16,
                                  wireframe=False):
    """
    Returns a RGB colourspace volume visual geometry formatted as *JSON*.

    Parameters
    ----------
    colourspace : unicode, optional
        RGB colourspace used to generate the visual geometry.
    colourspace_model : unicode, optional
        Colourspace model used to generate the visual geometry.
    segments : int, optional
        Segments count per side of the *box* used to generate the visual
        geometry.
    wireframe : bool, optional
        Whether the visual geometry must represent a wireframe visual.

    Returns
    -------
    unicode
        RGB colourspace volume visual geometry formatted as *JSON*.
    """

    colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(re.escape(colourspace))))

    cube = create_box(
        width_segments=segments,
        height_segments=segments,
        depth_segments=segments)

    vertices = cube[0]['position'] + 0.5
    faces = colourspace_model_faces_reorder(
        np.reshape(cube[1], (-1, 1)), colourspace_model)
    RGB = cube[0]['colour']

    XYZ = RGB_to_XYZ(vertices, colourspace.whitepoint, colourspace.whitepoint,
                     colourspace.RGB_to_XYZ_matrix)
    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 colourspace_model), colourspace_model)

    return buffer_geometry(position=vertices, color=RGB, index=faces)


def spectral_locus_visual(colourspace=PRIMARY_COLOURSPACE,
                          colourspace_model=COLOURSPACE_MODEL,
                          cmfs='CIE 1931 2 Degree Standard Observer'):
    """
    Returns the spectral locus visual geometry formatted as *JSON*.

    Parameters
    ----------
    colourspace : unicode, optional
        RGB colourspace used to generate the visual geometry.
    colourspace_model : unicode, optional
        Colourspace model used to generate the visual geometry.
    cmfs : unicode, optional
        Standard observer colour matching functions used to draw the spectral
        locus.

    Returns
    -------
    unicode
        Spectral locus visual geometry formatted as *JSON*.
    """

    colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(re.escape(colourspace))))

    cmfs = first_item(filter_cmfs(cmfs))
    XYZ = cmfs.values

    XYZ = np.vstack((XYZ, XYZ[0, ...]))

    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 colourspace_model), colourspace_model)

    RGB = normalise_maximum(
        XYZ_to_RGB(XYZ, colourspace.whitepoint, colourspace.whitepoint,
                   colourspace.XYZ_to_RGB_matrix),
        axis=-1)

    return buffer_geometry(position=vertices, color=RGB)


def RGB_image_scatter_visual(path,
                             primary_colourspace=PRIMARY_COLOURSPACE,
                             secondary_colourspace=SECONDARY_COLOURSPACE,
                             image_colourspace=IMAGE_COLOURSPACE,
                             image_decoding_cctf=IMAGE_DECODING_CCTF,
                             colourspace_model=COLOURSPACE_MODEL,
                             out_of_primary_colourspace_gamut=False,
                             out_of_secondary_colourspace_gamut=False,
                             sub_sampling=25,
                             saturate=False):
    """
    Returns a RGB image scatter visual geometry formatted as *JSON* for
    given image.

    Parameters
    ----------
    path : unicode
        Server side path of the image to read to generate the scatter points.
    primary_colourspace : unicode, optional
        Primary RGB colourspace used to generate the visual geometry.
    secondary_colourspace: unicode, optional
        Secondary RGB colourspace used to generate the visual geometry.
    image_colourspace: unicode, optional
        **{'Primary', 'Secondary'}**,
        Analysed image RGB colourspace.
    image_decoding_cctf : unicode, optional
        Analysed image decoding colour component transfer function
        (Decoding CCTF) / electro-optical transfer function (EOTF / EOCF) that
        maps an :math:`R'G'B'` video component signal value to tristimulus
        values at the display.
    colourspace_model : unicode, optional
        Colourspace model used to generate the visual geometry.
    out_of_primary_colourspace_gamut : bool, optional
        Whether to only generate the out of primary RGB colourspace gamut
        visual geometry.
    out_of_secondary_colourspace_gamut : bool, optional
        Whether to only generate the out of secondary RGB colourspace gamut
        visual geometry.
    sub_sampling : int, optional
        Consider every ``sub_sampling`` pixels of the image to generate the
        visual geometry. Using a low number will yield a large quantity of
        points, e.g. *1* yields *2073600* points for a *1080p* image.
    saturate : bool, optional
        Whether to clip the image in domain [0, 1].

    Returns
    -------
    unicode
        RGB image scatter visual geometry formatted as *JSON*.
    """

    primary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(primary_colourspace))))
    secondary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(secondary_colourspace))))

    colourspace = (primary_colourspace if image_colourspace == 'Primary' else
                   secondary_colourspace)

    RGB = load_image(path, image_decoding_cctf)

    if saturate:
        RGB = np.clip(RGB, 0, 1)

    RGB = RGB[..., 0:3].reshape(-1, 3)[::sub_sampling]

    if out_of_primary_colourspace_gamut:
        RGB_c = np.copy(RGB)

        if image_colourspace == 'Secondary':
            RGB_c = RGB_to_RGB(RGB, secondary_colourspace, primary_colourspace)

        RGB = RGB[np.any(np.logical_or(RGB_c < 0, RGB_c > 1), axis=-1)]

    if out_of_secondary_colourspace_gamut:
        RGB_c = np.copy(RGB)

        if image_colourspace == 'Primary':
            RGB_c = RGB_to_RGB(RGB, primary_colourspace, secondary_colourspace)

        RGB = RGB[np.any(np.logical_or(RGB_c < 0, RGB_c > 1), axis=-1)]

    XYZ = RGB_to_XYZ(RGB, colourspace.whitepoint, colourspace.whitepoint,
                     colourspace.RGB_to_XYZ_matrix)
    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 colourspace_model), colourspace_model)

    if out_of_primary_colourspace_gamut or out_of_secondary_colourspace_gamut:
        RGB = np.ones(RGB.shape)

    return buffer_geometry(position=vertices, color=RGB)


def image_data(path,
               primary_colourspace=PRIMARY_COLOURSPACE,
               secondary_colourspace=SECONDARY_COLOURSPACE,
               image_colourspace=IMAGE_COLOURSPACE,
               image_decoding_cctf=IMAGE_DECODING_CCTF,
               out_of_primary_colourspace_gamut=False,
               out_of_secondary_colourspace_gamut=False,
               saturate=False):
    """
    Returns given image RGB data or its out of gamut values formatted as
    *JSON*.

    Parameters
    ----------
    path : unicode
        Server side path of the image to read.
    primary_colourspace : unicode, optional
        Primary RGB colourspace used to generate out of gamut values.
    secondary_colourspace: unicode, optional
        Secondary RGB colourspace used to generate out of gamut values.
    image_colourspace: unicode, optional
        **{'Primary', 'Secondary'}**,
        Analysed image RGB colourspace.
    image_decoding_cctf : unicode, optional
        Analysed image decoding colour component transfer function
        (Decoding CCTF) / electro-optical transfer function (EOTF / EOCF) that
        maps an :math:`R'G'B'` video component signal value to tristimulus
        values at the display.
    out_of_primary_colourspace_gamut : bool, optional
        Whether to only generate the out of primary RGB colourspace gamut
        values.
    out_of_secondary_colourspace_gamut : bool, optional
        Whether to only generate the out of secondary RGB colourspace gamut
        value.
    saturate : bool, optional
        Whether to clip the image in domain [0, 1].

    Returns
    -------
    unicode
        RGB image data or its out of gamut values formatted as *JSON*.
    """

    primary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(primary_colourspace))))
    secondary_colourspace = first_item(
        filter_RGB_colourspaces('^{0}$'.format(
            re.escape(secondary_colourspace))))

    RGB = load_image(path, image_decoding_cctf)

    if saturate:
        RGB = np.clip(RGB, 0, 1)

    if out_of_primary_colourspace_gamut:
        if image_colourspace == 'Secondary':
            RGB = RGB_to_RGB(RGB, secondary_colourspace, primary_colourspace)

        RGB[np.logical_and(RGB >= 0, RGB <= 1)] = 0
        RGB[RGB != 0] = 1
        RGB[np.any(RGB == 1, axis=-1)] = 1

    if out_of_secondary_colourspace_gamut:
        if image_colourspace == 'Primary':
            RGB = RGB_to_RGB(RGB, primary_colourspace, secondary_colourspace)

        RGB[np.logical_and(RGB >= 0, RGB <= 1)] = 0
        RGB[RGB != 0] = 1
        RGB[np.any(RGB == 1, axis=-1)] = 1

    shape = RGB.shape
    RGB = np.ravel(RGB[..., 0:3].reshape(-1, 3))
    RGB = np.around(RGB, np.finfo(DEFAULT_FLOAT_DTYPE).precision)

    return json.dumps({
        'width': shape[1],
        'height': shape[0],
        'data': RGB.tolist()
    })
