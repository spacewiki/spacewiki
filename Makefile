IMAGES 	:= $(wildcard theme/img/*)

IMAGES_OUT 	:= $(patsubst theme/img/%,static/img/%,$(IMAGES))

.PHONY: test all static syncdb

all: static syncdb

static: images

syncdb:
	./manage.py db syncdb

check: test

test:
	nosetests --with-coverage

docker_test:
	pip install nose
	nosetests --with-coverage

lint:
	pylint -f html *.py | tee linter.html

clean:
	rm -f $(IMAGES_OUT)

images: static/img $(IMAGES_OUT)

static/img static/lib:
	mkdir -p $@

static/img/%.png: theme/img/%.png
	pngcrush $< $@

static/img/%.gif: theme/img/%.gif
	gifsicle < $< > $@

static/img/%.svg: theme/img/%.svg
	cp $< $@
