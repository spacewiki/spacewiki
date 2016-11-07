FROM fedora:24
EXPOSE 5000
WORKDIR /spacewiki/app/
VOLUME /data

RUN dnf -y update && \
    dnf install -y ruby rubygems && \
    gem install pups

ADD docker/ /spacewiki/docker/
ADD docker/build.yaml /spacewiki/pups/build.yaml

ADD docker/docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["runserver"]

ADD . /spacewiki/git/
RUN cat /spacewiki/docker/git.yaml /spacewiki/docker/build.yaml | pups --stdin
