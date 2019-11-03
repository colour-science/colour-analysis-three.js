FROM python:3.6

WORKDIR /tmp
COPY ./requirements.txt /tmp
RUN pip install -r requirements.txt \
    && rm /tmp/requirements.txt

ARG CACHE_DATE

RUN mkdir -p /home/colour-analysis
WORKDIR /home/colour-analysis
COPY . /home/colour-analysis

CMD sh -c 'if [ -z "${SSL_CERTIFICATE}" ]; then \
    gunicorn --log-level debug -b 0.0.0.0:5000 app:APP; else \
    gunicorn --certfile "${SSL_CERTIFICATE}" --keyfile "${SSL_KEY}" --log-level debug -b 0.0.0.0:5000 app:APP; fi'
