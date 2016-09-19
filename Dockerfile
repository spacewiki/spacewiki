FROM fedora:24

EXPOSE 5000
WORKDIR /srv/spacewiki/app/
VOLUME /srv/spacewiki/shared

RUN mkdir -p /srv/spacewiki/

RUN dnf -y update

RUN dnf install -y git python-devel gifsicle ruby rubygem-sass uglify-js \
        pngcrush make python-pillow python-psycopg2 python-gunicorn \
        python-greenlet && \
    dnf clean all

COPY requirements.txt /srv/spacewiki/app/requirements.txt
RUN pip install -r /srv/spacewiki/app/requirements.txt && \
    rm -rf /root/.cache

ADD . /srv/spacewiki/app

ADD docker_settings.py /srv/spacewiki/app/local_settings.py
ADD /docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

RUN make static

ENTRYPOINT ["/docker-entrypoint.sh"]
