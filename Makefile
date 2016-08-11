upload:
	python setup.py sdist upload

test:
	rm -rf build
	tox -e py27
