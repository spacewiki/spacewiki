# SpaceWiki

[![Build Status](https://travis-ci.org/tdfischer/spacewiki.svg?branch=master)](https://travis-ci.org/tdfischer/spacewiki)

All wiki software sucks. SpaceWiki sucks less than most.

I've been involved with building hackerspaces for the last ~5 years or so. Every
space has a wiki and more often than not it is MediaWiki.

For the longest time, I've wanted some sort of wiki that is tailored
specifically towards low-maintenence installs where nobody should rely on a
swarm of volunteers to curate, maintain, and otherwise write content. Wikipedia
has that and it works fantastic for them. Noisebridge does not and the wiki
tends to turn into a mess of outdated pages, broken images, and the like.
Entropy kills.

To see a live demo of SpaceWiki, [check out
ratchet.noisebridge.systems](http://ratchet.noisebridge.systems/wiki/)

## Features

SpaceWiki has an exceptionally tiny feature set which should make it easy for
others to get up and going with minimal setup:

* Default sqlite database out of the box
* Markdown page syntax
* The familiar MediaWiki syntax for linking to other pages
* Softlinks for easy-peasy organic discovery of related pages. If you are
  unfamiliar with Softlinks, [check out how Everything2 does
  it](http://everything2.com/title/Soft+link)

## Docker Installation

spacewiki is distributed as a Docker container. To use:

    $ docker run -v /srv/spacewiki:/data -p 5000:5000 tdfischer/spacewiki

The Docker container starts ./manage.py runserver, which defaults to serving
spacewiki on 0.0.0.0:5000. The app is installed in /spacewiki/, and all
persistent data/configuration is in /data.

## wsgi Notes

The recommended way to run spacewiki is with Docker, but there is nothing
stopping you from running it on your own. Spacewiki uses flask + peewee and aims
to keep a minimal set of dependencies. The UI uses Foundation and requires
building with sass + uglifyjs + gifsicle + pngcrush.

### Setup

    $ make
    $ ./manage.py runserver

### Dependencies

* gifsicle
* pngcrush
* sass >= 3.4.3
* uglifyjs

## TODO

* Support more than sqlite
* Image uploads
* Crazy easy "attach photo" button for use with a mobile device/camera

## License

SpaceWiki is released under the terms of the GNU Affero General Public License v3

![AGPLv3](https://raw.github.com/tdfischer/spacewiki/master/doc/agpl.png)
