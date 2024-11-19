# -*- coding: utf-8 -*-
"""
Application
===========
"""

from __future__ import division, unicode_literals

import json
import os
from cachelib import SimpleCache
from flask import Flask, Response, render_template, request
from flask_caching import Cache
from flask_compress import Compress

from colour.utilities import domain_range_scale

from colour_analysis import (
    COLOURSPACE_MODEL, IMAGE_COLOURSPACE, IMAGE_CCTF_DECODING,
    PRIMARY_COLOURSPACE, RGB_colourspaces, RGB_colourspace_volume_visual,
    RGB_image_scatter_visual, SECONDARY_COLOURSPACE, colourspace_models,
    cctf_decodings, image_data, pointer_gamut_visual, spectral_locus_visual,
    visible_spectrum_visual)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2018-2021 - Colour Developers'
__license__ = 'New BSD License - https://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-developers@colour-science.org'
__status__ = 'Production'

__application_name__ = 'Colour - Analysis'

__major_version__ = '0'
__minor_version__ = '1'
__change_version__ = '8'
__version__ = '.'.join(
    (__major_version__,
     __minor_version__,
     __change_version__))  # yapf: disable


__all__ = [
    'APP', 'CACHE', 'CACHE_DEFAULT_TIMEOUT', 'IMAGES_DIRECTORY',
    'images_response', 'cctf_decodings_response',
    'colourspace_models_response', 'RGB_colourspaces_response',
    'image_data_response', 'RGB_colourspace_volume_visual_response',
    'RGB_image_scatter_visual_response', 'spectral_locus_visual_response',
    'pointer_gamut_visual_response', 'index', 'after_request'
]

APP = Flask(__name__)
"""
*Flask* app.

APP : Flask
"""

CACHE = Cache(config={'CACHE_TYPE': 'simple'})
"""
Global application responses cache.

CACHE : Cache
"""

CACHE_DEFAULT_TIMEOUT = 60 * 24 * 7
"""
Cache responses timeout.

CACHE_DEFAULT_TIMEOUT : int
"""

CACHE.init_app(APP)

APP.config.update(
    COMPRESS_LEVEL=3,
    COMPRESS_CACHE_KEY=lambda x: x.full_path,
    COMPRESS_CACHE_BACKEND=lambda: SimpleCache(default_timeout=  # noqa
                                               CACHE_DEFAULT_TIMEOUT),
)

Compress(APP)

IMAGES_DIRECTORY = os.path.join(os.getcwd(), 'static', 'images')
"""
Images directory.

IMAGES_DIRECTORY : unicode
"""


def _null_to_None(data):
    """
    Converts *Javascript* originated *null* and *undefined* strings
    to `None`. Non-matching data will be passed untouched.

    Parameters
    ----------
    data : unicode
        Data to convert.

    Returns
    -------
    None or unicode
        Converted data.
    """

    if data in ('null', 'undefined'):
        return None
    else:
        return data


def _bool_to_bool(data):
    """
    Converts *Javascript* originated *true* and *false* strings
    to `True` or `False`. Non-matching data will be passed untouched.

    Parameters
    ----------
    data : unicode
        Data to convert.

    Returns
    -------
    True or False or unicode
        Converted data.
    """

    if data == 'true' or data is True:
        return True
    elif data == 'false' or data is False:
        return False
    else:
        return data


@APP.route('/images')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def images_response():
    """
    Returns the images response.

    Returns
    -------
    Response
        Images response.
    """

    json_data = json.dumps(sorted(os.listdir(IMAGES_DIRECTORY)))

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/decoding-cctfs')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def cctf_decodings_response():
    """
    Returns the decoding colour component transfer functions response.

    Returns
    -------
    Response
        Decoding colour component transfer functions response.
    """

    json_data = cctf_decodings()

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/colourspace-models')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def colourspace_models_response():
    """
    Returns the colourspace models response.

    Returns
    -------
    Response
        Colourspace models response.
    """

    json_data = colourspace_models()

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/RGB-colourspaces')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def RGB_colourspaces_response():
    """
    Returns the RGB colourspaces response.

    Returns
    -------
    Response
        RGB colourspaces response.
    """

    json_data = RGB_colourspaces()

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/image-data/<image>')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def image_data_response(image):
    """
    Returns an image data response.

    Returns
    -------
    Response
        Image data response.
    """

    path = os.path.join(os.getcwd(), 'static', 'images', image)

    args = request.args
    json_data = image_data(
        path=path,
        primary_colourspace=args.get('primaryColourspace',
                                     PRIMARY_COLOURSPACE),
        secondary_colourspace=args.get('secondaryColourspace',
                                       SECONDARY_COLOURSPACE),
        image_colourspace=args.get('imageColourspace', IMAGE_COLOURSPACE),
        image_decoding_cctf=args.get('imageDecodingCctf', IMAGE_CCTF_DECODING),
        out_of_primary_colourspace_gamut=_bool_to_bool(
            args.get('outOfPrimaryColourspaceGamut', False)),
        out_of_secondary_colourspace_gamut=_bool_to_bool(
            args.get('outOfSecondaryColourspaceGamut', False)),
        out_of_pointer_gamut=_bool_to_bool(args.get('outOfPointerGamut',
                                                    False)),
        saturate=_bool_to_bool(args.get('saturate', False)))

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/RGB-colourspace-volume-visual')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def RGB_colourspace_volume_visual_response():
    """
    Returns a RGB colourspace volume visual response.

    Returns
    -------
    Response
         RGB colourspace volume visual response.
    """

    args = request.args
    json_data = RGB_colourspace_volume_visual(
        colourspace=args.get('colourspace', PRIMARY_COLOURSPACE),
        colourspace_model=args.get('colourspaceModel', COLOURSPACE_MODEL),
        segments=int(args.get('segments', 16)),
        wireframe=_bool_to_bool(args.get('wireframe', False)),
    )

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/RGB-image-scatter-visual/<image>')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def RGB_image_scatter_visual_response(image):
    """
    Returns a RGB image scatter visual response.

    Returns
    -------
    Response
        RGB image scatter visual response.
    """

    path = os.path.join(os.getcwd(), 'static', 'images', image)

    args = request.args
    json_data = RGB_image_scatter_visual(
        path=path,
        primary_colourspace=args.get('primaryColourspace',
                                     PRIMARY_COLOURSPACE),
        secondary_colourspace=args.get('secondaryColourspace',
                                       SECONDARY_COLOURSPACE),
        image_colourspace=args.get('imageColourspace', IMAGE_COLOURSPACE),
        image_decoding_cctf=args.get('imageDecodingCctf', IMAGE_CCTF_DECODING),
        colourspace_model=args.get('colourspaceModel', COLOURSPACE_MODEL),
        out_of_primary_colourspace_gamut=_bool_to_bool(
            args.get('outOfPrimaryColourspaceGamut', False)),
        out_of_secondary_colourspace_gamut=_bool_to_bool(
            args.get('outOfSecondaryColourspaceGamut', False)),
        out_of_pointer_gamut=_bool_to_bool(args.get('outOfPointerGamut',
                                                    False)),
        sub_sampling=int(args.get('subSampling', 25)),
        saturate=_bool_to_bool(args.get('saturate', False)),
    )

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/spectral-locus-visual')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def spectral_locus_visual_response():
    """
    Returns a spectral locus visual response.

    Returns
    -------
    Response
        Spectral locus visual response.
    """

    args = request.args
    json_data = spectral_locus_visual(
        colourspace=args.get('colourspace', PRIMARY_COLOURSPACE),
        colourspace_model=args.get('colourspaceModel', COLOURSPACE_MODEL),
    )

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/pointer-gamut-visual')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def pointer_gamut_visual_response():
    """
    Returns a *Pointer's Gamut* visual response.

    Returns
    -------
    Response
        *Pointer's Gamut* visual response.
    """

    args = request.args
    json_data = pointer_gamut_visual(colourspace_model=args.get(
        'colourspaceModel', COLOURSPACE_MODEL), )

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/visible-spectrum-visual')
@CACHE.cached(timeout=CACHE_DEFAULT_TIMEOUT, query_string=True)
def visible_spectrum_visual_response():
    """
    Returns the visible spectrum visual response.

    Returns
    -------
    Response
        visible spectrum visual response.
    """

    args = request.args
    json_data = visible_spectrum_visual(colourspace_model=args.get(
        'colourspaceModel', COLOURSPACE_MODEL), )

    response = Response(json_data, status=200, mimetype='application/json')
    response.headers['X-Content-Length'] = len(json_data)

    return response


@APP.route('/')
def index():
    """
    Returns the index response.

    Returns
    -------
    Response
        Index response.
    """

    return render_template('index.html',
                           colour_analysis_js=os.environ.get(
                               'COLOUR_ANALYSIS_JS',
                               '/static/js/colour-analysis.js'),
                           image=sorted(os.listdir(IMAGES_DIRECTORY))[0],
                           primary_colourspace=PRIMARY_COLOURSPACE,
                           secondary_colourspace=SECONDARY_COLOURSPACE,
                           image_colourspace=IMAGE_COLOURSPACE,
                           image_decoding_cctf=IMAGE_CCTF_DECODING,
                           colourspace_model=COLOURSPACE_MODEL)


@APP.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'X-Content-Length')

    return response


if __name__ == '__main__':
    with domain_range_scale(1):
        APP.run()
