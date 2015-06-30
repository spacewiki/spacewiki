FROM fedora:22

EXPOSE 5000
WORKDIR /srv/spacewiki/

RUN dnf -y update && \
    dnf install -y gcc git python-devel gifsicle ruby rubygem-sass uglify-js pngcrush make && \
    mkdir -p /srv/spacewiki/ && \
    dnf clean all

COPY requirements.txt /srv/spacewiki/requirements.txt
RUN pip install -r /srv/spacewiki/requirements.txt && \
    rm -rf /root/.cache

ADD . /srv/spacewiki/

RUN make static

CMD ["/srv/spacewiki/manage.py", "runserver", "-h", "0.0.0.0"]
