PYTHON=python

ifdef PREFIX
PREFIX_ARG=--prefix=$(PREFIX)
else

NONLOCAL=$(shell $(PYTHON) -c 'from distutils.sysconfig import get_python_lib; print get_python_lib().startswith("/usr/lib")')
ifeq "$(NONLOCAL)" 'True'
PREFIX_ARG=--prefix=/usr/local
endif

endif

all: build

build:
	$(PYTHON) setup.py build
clean:
	$(PYTHON) setup.py clean --all
	find . -name '*.py[co]' -exec rm -f "{}" ';'
	find ./dnuos/locale -name '*.mo' -exec rm -f "{}" ';'
	rm -rf build dist dnuos.egg-info temp
install:
	$(PYTHON) setup.py install $(PREFIX_ARG)
