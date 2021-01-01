# -*- coding: utf-8 -*-
"""
Invoke - Tasks
==============
"""

import fileinput
import re
import sys
from invoke import task
from invoke.exceptions import Failure

from colour.utilities import message_box

import app

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2018-2021 - Colour Developers'
__license__ = 'New BSD License - https://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-developers@colour-science.org'
__status__ = 'Production'

__all__ = [
    'APPLICATION_NAME', 'ORG', 'CONTAINER', 'clean', 'quality', 'formatting',
    'npm_build', 'requirements', 'docker_build', 'docker_remove', 'docker_run'
]

APPLICATION_NAME = app.__application_name__

ORG = 'colourscience'

CONTAINER = APPLICATION_NAME.replace(' ', '').lower()


@task
def clean(ctx, bytecode=False):
    """
    Cleans the project.

    Parameters
    ----------
    bytecode : bool, optional
        Whether to clean the bytecode files, e.g. *.pyc* files.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Cleaning project...')

    patterns = []

    if bytecode:
        patterns.append('**/*.pyc')

    for pattern in patterns:
        ctx.run("rm -rf {}".format(pattern))


@task
def quality(ctx, flake8=True):
    """
    Checks the codebase with *Flake8*.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.
    flake8 : bool, optional
        Whether to check the codebase with *Flake8*.

    Returns
    -------
    bool
        Task success.
    """

    if flake8:
        message_box('Checking codebase with "Flake8"...')
        ctx.run('flake8')


@task
def formatting(ctx, yapf=True):
    """
    Formats the codebase with *Yapf*.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.
    yapf : bool, optional
        Whether to format the codebase with *Yapf*.

    Returns
    -------
    bool
        Task success.
    """

    if yapf:
        message_box('Formatting codebase with "Yapf"...')
        ctx.run('yapf -p -i -r .')


@task
def npm_build(ctx):
    """
    Builds the *npm* package.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Building "npm" package...')
    for package_file in ('package.json', 'package-lock.json'):
        version_found = False
        for line in fileinput.input(package_file, inplace=True):
            if re.match('\\s*"version": "[\\w.]+",',
                        line) and not version_found:
                line = '  "version": "{0}",\n'.format(app.__version__)
                version_found = True

            sys.stdout.write(line)

    ctx.run('npm run build')


@task
def requirements(ctx):
    """
    Exports the *requirements.txt* file.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Exporting "requirements.txt" file...')
    ctx.run('poetry run pip freeze | '
            'egrep -v '
            '"github.com/colour-science/colour-analysis-three.js|enum34" '
            '> requirements.txt')


@task(npm_build, requirements)
def docker_build(ctx):
    """
    Builds the *docker* image.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Building "docker" image...')

    ctx.run('docker build '
            '--build-arg CACHE_DATE="$(date)" '
            '-t {0}/{1}:latest -t {0}/{1}:v{2} .'.format(
                ORG, CONTAINER, app.__version__))


@task
def docker_remove(ctx):
    """
    Stops and remove the *docker* container.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Stopping "docker" container...')
    try:
        ctx.run('docker stop {0}'.format(CONTAINER))
    except Failure:
        pass

    message_box('Removing "docker" container...')
    try:
        ctx.run('docker rm {0}'.format(CONTAINER))
    except Failure:
        pass


@task(docker_remove, docker_build)
def docker_run(ctx):
    """
    Runs the *docker* container.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Running "docker" container...')
    ctx.run('docker run -d '
            '--name={1} '
            '-p 8020:5000 {0}/{1}'.format(ORG, CONTAINER))


@task
def docker_push(ctx):
    """
    Pushes the *docker* container.

    Parameters
    ----------
    ctx : invoke.context.Context
        Context.

    Returns
    -------
    bool
        Task success.
    """

    message_box('Pushing "docker" container...')
    ctx.run('docker push {0}/{1}'.format(ORG, CONTAINER))
