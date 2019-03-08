PYTHON=python3.5
PYTHON_VENV=env

$(PYTHON_VENV)/.created: REQUIREMENTS.dev.txt
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install -r ./REQUIREMENTS.dev.txt && \
	date > $(PYTHON_VENV)/.created

env: $(PYTHON_VENV)/.created

clean:
	rm -rf $(PYTHON_VENV)

test: env
	. $(PYTHON_VENV)/bin/activate && \
	tox

ci-test: env
	. $(PYTHON_VENV)/bin/activate && \
	JENKINS_URL=1 tox

edit: env
	. $(PYTHON_VENV)/bin/activate && \
	$$EDITOR

shell: env
	. $(PYTHON_VENV)/bin/activate && \
	ipython

freeze: env
	. $(PYTHON_VENV)/bin/activate && \
	pip freeze

test-site: env
	. $(PYTHON_VENV)/bin/activate && \
	rm -rf test-site && \
	flamingo init test-site debug=True

server: test-site
	cd test-site && \
	make server
