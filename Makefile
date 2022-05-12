PYTHON=python3
PYTHON_VENV=env

$(PYTHON_VENV)/.created: REQUIREMENTS.dev.txt
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r ./REQUIREMENTS.dev.txt && \
	date > $(PYTHON_VENV)/.created

env: $(PYTHON_VENV)/.created

clean:
	rm -rf $(PYTHON_VENV)

lint: env
	. $(PYTHON_VENV)/bin/activate && \
	tox -e lint

lazy-test: env
	. $(PYTHON_VENV)/bin/activate && \
	tox $(args)

test: env
	. $(PYTHON_VENV)/bin/activate && \
	rm -rf flamingo.egg-info dist build && \
	tox -r $(args)

ci-test: env
	. $(PYTHON_VENV)/bin/activate && \
	EXTENDED_BUILD_TESTS=1 JENKINS_URL=1 tox -r $(args)

shell: env
	. $(PYTHON_VENV)/bin/activate && \
	rlpython

freeze: env
	. $(PYTHON_VENV)/bin/activate && \
	pip freeze

test-site: env
	. $(PYTHON_VENV)/bin/activate && \
	rm -rf test-site && \
	flamingo init test-site debug=True $(args)

server: test-site
	cd test-site && \
	make server

sdist: env
	. $(PYTHON_VENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	./setup.py sdist

_release: sdist
	. $(PYTHON_VENV)/bin/activate && \
	twine upload dist/*

.PHONY: test-site
