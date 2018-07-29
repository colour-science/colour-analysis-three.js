import os
import hashlib
from flask import Flask, render_template, make_response, request
from io import BytesIO
from werkzeug.contrib.cache import SimpleCache

from colour.utilities import domain_range_scale

from colour_analysis import (
    COLOURSPACE_MODEL, IMAGE_COLOURSPACE, PRIMARY_COLOURSPACE,
    RGB_colourspaces, RGB_colourspace_volume_visual, SECONDARY_COLOURSPACE,
    colourspace_models, spectral_locus_visual, RGB_image_scatter_visual,
    image_data)

APP = Flask(__name__)

APP_CACHE = SimpleCache(default_timeout=1440)


def _null_to_None(data):
    if data in ('null', 'undefined'):
        return None
    else:
        return data


def _bool_to_bool(data):
    if data == 'true' or data is True:
        return True
    elif data == 'false' or data is False:
        return False
    else:
        raise ValueError('Value must be "true" or "false"!')


def _hash(data):
    return hashlib.sha1(str(data)).hexdigest()


def from_cache(key, callable):
    data = APP_CACHE.get(key)
    if data is None:
        data = callable()
        APP_CACHE.set(key, data)
    return data


@APP.route('/colourspace-models')
def colourspace_models_response():
    json_data = from_cache(_hash(request.full_path), colourspace_models)

    response = make_response(json_data)

    return response


@APP.route('/RGB-colourspaces')
def RGB_colourspaces_response():
    json_data = from_cache(_hash(request.full_path), RGB_colourspaces)

    response = make_response(json_data)

    return response


@APP.route('/RGB-colourspace-volume-visual')
def RGB_colourspace_volume_visual_response():
    args = request.args
    json_data = from_cache(
        _hash(request.full_path), lambda: RGB_colourspace_volume_visual(
            colourspace=args.get('colourspace', PRIMARY_COLOURSPACE),
            colourspace_model=args.get('colourspaceModel', COLOURSPACE_MODEL),
            segments=int(args.get('segments', 16)),
            uniform_colour=_null_to_None(args.get('uniformColour', None)),
            wireframe=_bool_to_bool(args.get('wireframe', False)),
            wireframe_colour=_null_to_None(args.get('wireframeColour', None)),
        ))

    response = make_response(json_data)

    return response


@APP.route('/spectral-locus-visual')
def spectral_locus_visual_response():
    args = request.args
    json_data = from_cache(
        _hash(request.full_path), lambda: spectral_locus_visual(
            colourspace=args.get('colourspace', PRIMARY_COLOURSPACE),
            colourspace_model=args.get('colourspaceModel', COLOURSPACE_MODEL),
            uniform_colour=_null_to_None(args.get('uniformColour', None)),
        ))

    response = make_response(json_data)

    return response


@APP.route('/RGB-image-scatter-visual/<image>')
def RGB_image_scatter_visual_response(image):
    path = os.path.join(os.getcwd(), 'static', 'images', image)

    args = request.args
    json_data = from_cache(
        _hash(request.full_path), lambda: RGB_image_scatter_visual(
            path=path,
            primary_colourspace=args.get('primaryColourspace',
                                         PRIMARY_COLOURSPACE),
            secondary_colourspace=args.get('secondaryColourspace',
                                           SECONDARY_COLOURSPACE),
            image_colourspace=args.get('imageColourspace', IMAGE_COLOURSPACE),
            colourspace_model=args.get('colourspaceModel', COLOURSPACE_MODEL),
            uniform_colour=_null_to_None(args.get('uniformColour', None)),
            sub_sampling=int(args.get('subSampling', 25)),
            saturate=_bool_to_bool(args.get('saturate', False)),
        ))

    response = make_response(json_data)

    return response


@APP.route('/image-data/<image>')
def image_data_response(image):
    path = os.path.join(os.getcwd(), 'static', 'images', image)

    args = request.args
    json_data = from_cache(
        _hash(request.full_path), lambda: image_data(
            path=path,
            primary_colourspace=args.get('primaryColourspace',
                                         PRIMARY_COLOURSPACE),
            secondary_colourspace=args.get('secondaryColourspace',
                                           SECONDARY_COLOURSPACE),
            image_colourspace=args.get('imageColourspace', IMAGE_COLOURSPACE),
            out_of_primary_colourspace_gamut=_bool_to_bool(args.get(
                'outOfPrimaryColourspaceGamut', False)),
            out_of_secondary_colourspace_gamut=_bool_to_bool(args.get(
                'outOfSecondaryColourspaceGamut', False)),
            saturate=_bool_to_bool(args.get('saturate', False))))

    response = make_response(json_data)

    return response


@APP.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with domain_range_scale(1):
        APP.run(debug=True)
