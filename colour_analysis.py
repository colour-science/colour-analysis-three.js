# -*- coding: utf-8 -*-
"""
Colour - Analysis
=================

Defines various objects that typically output the geometry as JSON to be
loaded by "Three.js".
"""

import json
import numpy as np
import os
import re
from cachelib import SimpleCache

from colour import (CCS_ILLUMINANTS, CCTF_DECODINGS, Lab_to_XYZ, LCHab_to_Lab,
                    RGB_COLOURSPACES, RGB_to_RGB, RGB_to_XYZ, XYZ_to_RGB,
                    XYZ_to_JzAzBz, XYZ_to_OSA_UCS, convert,
                    is_within_pointer_gamut, read_image)
from colour.geometry import primitive_cube
from colour.models import (CCS_ILLUMINANT_POINTER_GAMUT,
                           DATA_POINTER_GAMUT_VOLUME, linear_function)
from colour.plotting import filter_cmfs, filter_RGB_colourspaces
from colour.utilities import (as_float_array, first_item, normalise_maximum,
                              tsplit, tstack)
from colour.volume import XYZ_outer_surface

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2018-2021 - Colour Developers'
__license__ = 'New BSD License - https://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-developers@colour-science.org'
__status__ = 'Production'

__all__ = [
    'LINEAR_FILE_FORMATS', 'DTYPE_POSITION', 'DTYPE_COLOUR',
    'COLOURSPACE_MODELS', 'COLOURSPACE_MODEL_LABELS', 'PRIMARY_COLOURSPACE',
    'SECONDARY_COLOURSPACE', 'IMAGE_COLOURSPACE', 'IMAGE_CCTF_DECODING',
    'COLOURSPACE_MODEL', 'IMAGE_CACHE', 'load_image',
    'XYZ_to_colourspace_model', 'colourspace_model_axis_reorder',
    'colourspace_model_faces_reorder', 'cctf_decodings', 'colourspace_models',
    'RGB_colourspaces', 'buffer_geometry', 'conform_primitive_dtype',
    'image_data', 'RGB_colourspace_volume_visual', 'spectral_locus_visual',
    'RGB_image_scatter_visual', 'pointer_gamut_visual',
    'visible_spectrum_visual'
]

LINEAR_FILE_FORMATS = ('.exr', '.hdr')
"""
Assumed linear image formats.

LINEAR_IMAGE_FORMATS : tuple
"""

DTYPE_POSITION = np.sctypeDict.get(
    os.environ.get('COLOUR_SCIENCE__COLOUR_ANALYSIS_DTYPE_POSITION',
                   'float32'))
"""
Default floating point number dtype for visual data except colour. "float32" is
usually chosen over "float16" or "float64" as a good compromise between
precision and data size.

DTYPE_POSITION : type
"""

DTYPE_COLOUR = np.sctypeDict.get(
    os.environ.get('COLOUR_SCIENCE__COLOUR_ANALYSIS_DTYPE_COLOUR', 'float16'))
"""
Default floating point number dtype for visual colour and image data. "float16"
is usually chosen over "float32" and "float64" because it is lighter and thus
more adapted to send data from the server to client.

DTYPE_COLOUR : type
"""

COLOURSPACE_MODELS = ('CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD',
                      'CAM16SCD', 'CAM16UCS', 'CIE XYZ', 'CIE xyY', 'CIE Lab',
                      'CIE Luv', 'CIE UCS', 'CIE UVW', 'DIN 99', 'Hunter Lab',
                      'Hunter Rdab', 'ICTCP', 'IGPGTG', 'IPT', 'JzAzBz',
                      'OSA UCS', 'hdr-CIELAB', 'hdr-IPT')
"""
Reference colourspace models defining available colour transformations from
CIE XYZ tristimulus values.

COLOURSPACE_MODELS : tuple
    **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD', 'CAM16UCS',
    'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW', 'DIN 99',
    'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG', 'IPT', 'JzAzBz', 'OSA UCS',
    'hdr-CIELAB', 'hdr-IPT'}**
"""

COLOURSPACE_MODEL_LABELS = {
    'CAM02LCD': ('M', 'J', 'h'),
    'CAM02SCD': ('M', 'J', 'h'),
    'CAM02UCS': ('M', 'J', 'h'),
    'CAM16LCD': ('M', 'J', 'h'),
    'CAM16SCD': ('M', 'J', 'h'),
    'CAM16UCS': ('M', 'J', 'h'),
    'CIE XYZ': ('X', 'Y', 'Z'),
    'CIE xyY': ('x', 'Y', 'y'),
    'CIE Lab': ('a*', 'L*', 'b*'),
    'CIE Luv': ('u*', 'L*', 'v*'),
    'CIE UCS': ('U', 'W', 'V'),
    'CIE UVW': ('U*', 'W*', 'V*'),
    'DIN 99': ('a99', 'L99', 'b99'),
    'Hunter Lab': ('a', 'L', 'b'),
    'Hunter Rdab': ('a', 'Rd', 'b'),
    'ICTCP': ('CT', 'I', 'CP'),
    'IGPGTG': ('PG', 'IG', 'TG'),
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
    **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD', 'CAM16UCS',
    'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW', 'DIN 99',
    'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG', 'IPT', 'JzAzBz', 'OSA UCS',
    'hdr-CIELAB', 'hdr-IPT'}**
"""

CCTF_DECODINGS.update({
    'Linear': linear_function,
})

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

IMAGE_CCTF_DECODING = 'sRGB'
"""
Analysed image RGB colourspace decoding colour component transfer function.

IMAGE_CCTF_DECODING : unicode
"""

COLOURSPACE_MODEL = 'CIE xyY'
"""
Analysis colour model.

COLOURSPACE_MODEL : unicode
    **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD', 'CAM16UCS',
    'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW', 'DIN 99',
    'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG', 'IPT', 'JzAzBz', 'OSA UCS',
    'hdr-CIELAB', 'hdr-IPT'}**
"""

DATA_POINTER_GAMUT = Lab_to_XYZ(
    LCHab_to_Lab(DATA_POINTER_GAMUT_VOLUME), CCS_ILLUMINANT_POINTER_GAMUT)
"""
Pointer's Gamut data converted to *CIE XYZ* tristimulus values.

DATA_POINTER_GAMUT : ndarray
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

    is_linear_image = os.path.splitext(path)[-1].lower() in LINEAR_FILE_FORMATS

    key = path if is_linear_image else '{0}-{1}'.format(path, decoding_cctf)

    RGB = IMAGE_CACHE.get(key)
    if RGB is None:
        RGB = read_image(path)

        if not is_linear_image:
            RGB = CCTF_DECODINGS[decoding_cctf](RGB)

        IMAGE_CACHE.set(key, RGB)

    return RGB


def XYZ_to_colourspace_model(XYZ, illuminant, model, **kwargs):
    """
    Converts from *CIE XYZ* tristimulus values to given colourspace model while
    normalising for visual convenience some of the models.

    Parameters
    ----------
    XYZ : array_like
        *CIE XYZ* tristimulus values.
    illuminant : array_like
        *CIE XYZ* tristimulus values *illuminant* *xy* chromaticity
        coordinates.
    model : unicode
        **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD',
        'CAM16UCS', 'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS',
        'CIE UVW', 'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG',
        'IPT', 'JzAzBz', 'OSA UCS', 'hdr-CIELAB', 'hdr-IPT'}**,
        Colourspace model to convert the *CIE XYZ* tristimulus values to.

    Other Parameters
    ----------------
    \\**kwargs : dict, optional
        Keywords arguments.

    Returns
    -------
    ndarray
        Colourspace model values.
    """

    ijk = convert(
        XYZ,
        'CIE XYZ',
        model,
        illuminant=illuminant,
        verbose={'mode': 'Short'},
        **kwargs)

    if model == 'JzAzBz':
        ijk /= XYZ_to_JzAzBz([1, 1, 1])[0]
    elif model == 'OSA UCS':
        ijk /= XYZ_to_OSA_UCS([1, 1, 1])[0]

    return ijk


def colourspace_model_axis_reorder(a, model=None):
    """
    Reorder the axes of given colourspace model :math:`a` array so that
    luminance is on *Y* axis.

    Parameters
    ----------
    a : array_like
        Colourspace model :math:`a` array.
    model : unicode, optional
        **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD',
        'CAM16UCS', 'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS',
        'CIE UVW', 'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG',
        'IPT', 'JzAzBz', 'OSA UCS', 'hdr-CIELAB', 'hdr-IPT'}**,
        Colourspace model.

    Returns
    -------
    ndarray
        Reordered colourspace model :math:`a` array.
    """

    i, j, k = tsplit(a)
    if model in ('CIE XYZ', ):
        a = tstack([k, j, i])
    elif model in ('CIE UCS', 'CIE UVW', 'CIE xyY'):
        a = tstack([j, k, i])
    elif model in ('CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD',
                   'CAM16UCS', 'CIE Lab', 'CIE LCHab', 'CIE Luv', 'CIE LCHuv',
                   'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG',
                   'IPT', 'JzAzBz', 'OSA UCS', 'hdr-CIELAB', 'hdr-IPT'):
        a = tstack([k, i, j])

    return a


def colourspace_model_faces_reorder(a, model=None):
    """
    Reorder the faces of given colourspace model :math:`a` array.

    Parameters
    ----------
    a : array_like
        Colourspace model :math:`a` array.
    model : unicode, optional
        **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD',
        'CAM16UCS', 'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS',
        'CIE UVW', 'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG',
        'IPT', 'JzAzBz', 'OSA UCS', 'hdr-CIELAB', 'hdr-IPT'}**,
        Colourspace model.

    Returns
    -------
    Figure
        Reordered colourspace model :math:`a` array.
    """

    if model in ('CIE XYZ', ):
        a = a[::-1]

    return a


def cctf_decodings():
    """
    Returns the decoding colour component transfer functions formatted as
    *JSON*.

    Returns
    -------
    unicode
        Decoding colour component transfer functions formatted as *JSON*.
    """

    return json.dumps(list(CCTF_DECODINGS.keys()))


def colourspace_models():
    """
    Returns the colourspace models formatted as *JSON*.

    Returns
    -------
    unicode
        Colourspace models formatted as *JSON*.
    """

    return json.dumps(COLOURSPACE_MODEL_LABELS)


def RGB_colourspaces():
    """
    Returns the RGB colourspaces formatted as *JSON*.

    Returns
    -------
    unicode
        RGB colourspaces formatted as *JSON*.
    """

    return json.dumps(list(RGB_COLOURSPACES.keys()))


def buffer_geometry(**kwargs):
    """
    Returns given geometry formatted as *JSON* compatible with *Three.js*
    `BufferGeometryLoader <https://threejs.org/docs/#api/loaders/\
BufferGeometryLoader>`__.

    Other Parameters
    ----------------
    \\**kwargs : dict, optional
        Valid attributes from `BufferGeometryLoader <https://threejs.org/docs/\
#api/loaders/BufferGeometryLoader>`__.

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
        dtype = values.dtype.name

        values = np.ravel(values)

        if 'float' in dtype:
            dtype = (DTYPE_COLOUR if attribute == 'color' else DTYPE_POSITION)
            values = np.around(values, np.finfo(dtype).precision)
            values = np.nan_to_num(values)
            dtype = np.dtype(dtype).name

        data['data']['attributes'][attribute] = {
            'itemSize': shape[-1],
            'type': data_types_conversion[dtype],
            'array': values.tolist()
        }

    return json.dumps(data)


def conform_primitive_dtype(primitive):
    """
    Conform the given primitive to the required dtype.

    Parameters
    ----------
    primitive : array_like
        Primitive to conform to the required dtype.

    Returns
    -------
    tuple
        Conformed primitive.
    """

    vertices, faces, outline = primitive

    return (
        vertices.astype(
            [('position', np.float32, (3, )), ('uv', np.float32, (2, )),
             ('normal', np.float32, (3, )), ('colour', np.float32, (4, ))]),
        faces.astype(np.uint32),
        outline.astype(np.uint32),
    )


def image_data(path,
               primary_colourspace=PRIMARY_COLOURSPACE,
               secondary_colourspace=SECONDARY_COLOURSPACE,
               image_colourspace=IMAGE_COLOURSPACE,
               image_decoding_cctf=IMAGE_CCTF_DECODING,
               out_of_primary_colourspace_gamut=False,
               out_of_secondary_colourspace_gamut=False,
               out_of_pointer_gamut=False,
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
        values.
    out_of_pointer_gamut : bool, optional
        Whether to only generate the out of *Pointer's Gamut* values.
    saturate : bool, optional
        Whether to clip the image in domain [0, 1].

    Returns
    -------
    unicode
        RGB image data or its out of gamut values formatted as *JSON*.
    """

    primary_colourspace = first_item(
        filter_RGB_colourspaces(re.escape(primary_colourspace)).values())
    secondary_colourspace = first_item(
        filter_RGB_colourspaces(re.escape(secondary_colourspace)).values())

    colourspace = (primary_colourspace if image_colourspace == 'Primary' else
                   secondary_colourspace)

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

    if out_of_pointer_gamut:
        O_PG = is_within_pointer_gamut(
            RGB_to_XYZ(
                RGB,
                colourspace.whitepoint,
                colourspace.whitepoint,
                colourspace.matrix_RGB_to_XYZ,
            )).astype(np.int_)
        O_PG = 1 - O_PG
        RGB[O_PG != 1] = 0
        RGB[O_PG == 1] = 1

    shape = RGB.shape
    RGB = np.ravel(RGB[..., 0:3].reshape(-1, 3))
    RGB = np.around(RGB, np.finfo(DTYPE_COLOUR).precision)

    return json.dumps({
        'width': shape[1],
        'height': shape[0],
        'data': RGB.tolist()
    })


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
        filter_RGB_colourspaces(re.escape(colourspace)).values())

    cube = conform_primitive_dtype(
        primitive_cube(
            width_segments=segments,
            height_segments=segments,
            depth_segments=segments))

    vertices = cube[0]['position'] + 0.5
    faces = colourspace_model_faces_reorder(
        np.reshape(cube[1], (-1, 1)), colourspace_model)
    RGB = cube[0]['colour']

    XYZ = RGB_to_XYZ(
        vertices,
        colourspace.whitepoint,
        colourspace.whitepoint,
        colourspace.matrix_RGB_to_XYZ,
    )
    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(
            XYZ,
            colourspace.whitepoint,
            colourspace_model,
        ), colourspace_model)

    return buffer_geometry(position=vertices, color=RGB, index=faces)


def RGB_image_scatter_visual(path,
                             primary_colourspace=PRIMARY_COLOURSPACE,
                             secondary_colourspace=SECONDARY_COLOURSPACE,
                             image_colourspace=IMAGE_COLOURSPACE,
                             image_decoding_cctf=IMAGE_CCTF_DECODING,
                             colourspace_model=COLOURSPACE_MODEL,
                             out_of_primary_colourspace_gamut=False,
                             out_of_secondary_colourspace_gamut=False,
                             out_of_pointer_gamut=False,
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
    out_of_pointer_gamut : bool, optional
        Whether to only generate the out of *Pointer's Gamut* visual geometry.
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
        filter_RGB_colourspaces(re.escape(primary_colourspace)).values())
    secondary_colourspace = first_item(
        filter_RGB_colourspaces(re.escape(secondary_colourspace)).values())

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

    if out_of_pointer_gamut:
        O_PG = is_within_pointer_gamut(
            RGB_to_XYZ(
                RGB,
                colourspace.whitepoint,
                colourspace.whitepoint,
                colourspace.matrix_RGB_to_XYZ,
            )).astype(np.int_)
        O_PG = 1 - O_PG
        RGB = RGB[O_PG == 1]

    XYZ = RGB_to_XYZ(
        RGB,
        colourspace.whitepoint,
        colourspace.whitepoint,
        colourspace.matrix_RGB_to_XYZ,
    )

    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(
            XYZ,
            colourspace.whitepoint,
            colourspace_model,
        ), colourspace_model)

    if (out_of_primary_colourspace_gamut or
            out_of_secondary_colourspace_gamut or out_of_pointer_gamut):
        RGB = np.ones(RGB.shape)

    return buffer_geometry(position=vertices, color=RGB)


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
        filter_RGB_colourspaces(re.escape(colourspace)).values())

    cmfs = first_item(filter_cmfs(cmfs).values())
    XYZ = cmfs.values

    XYZ = np.vstack([XYZ, XYZ[0, ...]])

    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(
            XYZ,
            colourspace.whitepoint,
            colourspace_model,
        ), colourspace_model)

    RGB = normalise_maximum(
        XYZ_to_RGB(
            XYZ,
            colourspace.whitepoint,
            colourspace.whitepoint,
            colourspace.matrix_XYZ_to_RGB,
        ),
        axis=-1)

    return buffer_geometry(position=vertices, color=RGB)


def pointer_gamut_visual(colourspace_model='CIE xyY'):
    """
    Returns the *Pointer's Gamut* visual geometry formatted as *JSON*.

    Parameters
    ----------
    colourspace_model : unicode, optional
        Colourspace model used to generate the visual geometry.

    Returns
    -------
    unicode
        *Pointer's Gamut* visual geometry formatted as *JSON*.
    """

    data_pointer_gamut = np.reshape(DATA_POINTER_GAMUT, (16, -1, 3))
    vertices = []
    for i in range(16):
        section = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                np.vstack(
                    [data_pointer_gamut[i], data_pointer_gamut[i][0, ...]]),
                CCS_ILLUMINANT_POINTER_GAMUT,
                colourspace_model,
            ), colourspace_model)

        vertices.append(list(zip(section, section[1:])))

    vertices = as_float_array(vertices)

    return buffer_geometry(position=vertices)


def visible_spectrum_visual(colourspace_model='CIE xyY'):
    """
    Returns the visible spectrum visual geometry formatted as *JSON*.

    Parameters
    ----------
    colourspace_model : unicode, optional
        Colourspace model used to generate the visual geometry.

    Returns
    -------
    unicode
        Visible spectrum visual geometry formatted as *JSON*.
    """

    XYZ = XYZ_outer_surface()
    vertices = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(
            XYZ,
            CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['E'],
            colourspace_model,
        ), colourspace_model)

    vertices = as_float_array(list(zip(vertices, vertices[1:])))

    return buffer_geometry(position=vertices)
