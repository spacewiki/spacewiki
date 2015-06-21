FROM fedora:22

EXPOSE 5000
WORKDIR /srv/spacewiki/

RUN dnf -y update && \
    dnf install -y gcc git python-devel gifsicle rubygem-sass uglify-js pngcrush make && \
    mkdir -p /srv/spacewiki/ 

COPY requirements.txt /srv/spacewiki/requirements.txt
RUN pip install -r /srv/spacewiki/requirements.txt

ADD . /srv/spacewiki/

RUN make static

CMD ["/srv/spacewiki/manage.py", "runserver"]
