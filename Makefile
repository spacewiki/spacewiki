IMAGES 	:= $(wildcard theme/img/*)

IMAGES_OUT 	:= $(patsubst theme/img/%,static/img/%,$(IMAGES))

.PHONY: test all static syncdb npm static_test

all: static syncdb

static: images npm

syncdb:
	./manage.py db syncdb

check: test

test: static_test
	nosetests --with-coverage

static_test: npm
	cd spacewiki/static/js/ && npm test

docker_test:
	pip install nose
	$(MAKE) test

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

npm:
	cd spacewiki/static/js && yarn install
