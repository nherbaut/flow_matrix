all : clean build buildp2


clean: clean-build clean-pyc 

clean-build:
		rm -fr build/
		rm -fr dist/
		rm -fr .eggs/
		find . -name '*.egg-info' -exec rm -fr {} +
		find . -name '*.egg' -exec rm -f {} +

clean-pyc:
		find . -name '*.pyc' -exec rm -f {} +
		find . -name '*.pyo' -exec rm -f {} +
		find . -name '*~' -exec rm -f {} +
		find . -name '__pycache__' -exec rm -fr {} +

install: clean
		python setup.py install

build:
	    .venv3/bin/python setup.py bdist_egg

buildp2:
	    .venv2/bin/python setup.py bdist_egg

docker:
		docker build . -t nherbaut/flowmatrix