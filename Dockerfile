FROM continuumio/miniconda

RUN apt-get update && \
    apt install -y \
        build-essential \
        cmake \
        libboost-all-dev \
        libbz2-dev \
        libgif-dev \
        libgl1-mesa-glx \
        libfreetype6-dev \
        libilmbase-dev \
        libjpeg-dev \
        libopenexr-dev \
        libpng-dev \
        libraw-dev \
        libtiff5-dev \
        libwebp-dev \
        qtbase5-dev && \
    apt-get clean

RUN cd /tmp && \
    wget https://github.com/OpenImageIO/oiio/archive/Release-1.8.13.tar.gz -O OpenImageIO-1.8.13.tar.gz && \
    tar -xvf OpenImageIO-1.8.13.tar.gz && \
    cd oiio-Release-1.8.13 && \
    make && \
    cp -r /tmp/oiio-Release-1.8.13/dist/linux64/bin/* /usr/local/bin/ && \
    cp -r /tmp/oiio-Release-1.8.13/dist/linux64/lib/* /usr/local/lib/ && \
    cp /tmp/oiio-Release-1.8.13/dist/linux64/lib/python2.7/site-packages/OpenImageIO.so /opt/conda/lib/python2.7/site-packages/

RUN /opt/conda/bin/conda install -y \
    flask \
    numpy \
    matplotlib \
    scipy \
    six
RUN pip install \
    gunicorn \
    Flask-Caching \
    git+git://github.com/colour-science/colour@develop \
    git+git://github.com/colour-science/flask-compress@feature/cache

RUN mkdir -p /home/colour-analysis
WORKDIR /home/colour-analysis
COPY . /home/colour-analysis

CMD sh -c 'if [ -z "${SSL_CERTIFICATE}" ]; then \
    gunicorn --log-level debug -b 0.0.0.0:5000 app:APP; else \
    gunicorn --certfile "${SSL_CERTIFICATE}" --keyfile "${SSL_KEY}" --log-level debug -b 0.0.0.0:5000 app:APP; fi'
