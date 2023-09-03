Colour - Analysis
=================

..  image:: https://www.colour-science.org/images/Colour_-_Analysis_-_Three.js.png

Introduction
------------

Image analysis tools based on `Colour <https://github.com/colour-science/colour>`__
and `Three.js <https://github.com/mrdoob/three.js>`__.

Installation
------------

Pull
~~~~

.. code-block:: bash

    $ docker pull colourscience/colour-analysis

Run
~~~

.. code-block:: bash

    $ docker run -d \
    --name=colour-analysis \
    -e COLOUR_ANALYSIS_JS=https://gitcdn.link/repo/colour-science/colour-analysis-three.js/master/dist/colour-analysis.js \
    -e COLOUR_SCIENCE__COLOUR_ANALYSIS_DTYPE_POSITION=float16 \
    -e COLOUR_SCIENCE__COLOUR_ANALYSIS_DTYPE_COLOUR=float16 \
    -v $IMAGES_DIRECTORY:/home/colour-analysis/static/images \
    -p 8020:5000 colourscience/colour-analysis

Development
-----------

.. code-block:: bash

    $ poetry install
    $ poetry run invoke docker-run

Code of Conduct
---------------

The *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,
is available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct>`__ page.

About
-----

| **Colour - Analysis** by Colour Developers
| Copyright 2018 – Colour Developers – `colour-developers@colour-science.org <colour-developers@colour-science.org>`__
| This software is released under terms of BSD-3-Clause: https://opensource.org/licenses/BSD-3-Clause
| `https://github.com/colour-science/colour-analysis-three.js <https://github.com/colour-science/colour-analysis-three.js>`__
