Colour - Analysis
=================

..  image:: https://www.colour-science.org/images/Colour_-_Analysis_-_Three.js.png

Introduction
------------

Image analysis tools based on `Colour <https://github.com/colour-science/colour>`_
and `Three.js <https://github.com/mrdoob/three.js/>`_.

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
    -e COLOUR_ANALYSIS_POSITION_DTYPE=Float16 \
    -e COLOUR_ANALYSIS_COLOUR_DTYPE=Float16 \
    -v $IMAGES_DIRECTORY:/home/colour-analysis/static/images \
    -p 8020:5000 colourscience/colour-analysis

Development
-----------

.. code-block:: bash

    $ conda create -y -n python-colour-analysis
    $ source activate python-colour-analysis
    $ conda install -y -c conda-forge colour-science
    $ conda install flask invoke matplotlib
    $ pip install git+git://github.com/colour-science/flask-compress@feature/cache
    $ npm run build
    $ python app.py

About
-----

| **Colour - Analysis** by Colour Developers
| Copyright © 2018 – Colour Developers – `colour-science@googlegroups.com <colour-science@googlegroups.com>`_
| This software is released under terms of New BSD License: http://opensource.org/licenses/BSD-3-Clause
| `http://github.com/colour-science/colour-analysis-three.js <http://github.com/colour-science/colour-analysis-three.js>`_
