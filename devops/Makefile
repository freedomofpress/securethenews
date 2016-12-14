all: molecule

.PHONY: clone
clone:
	if [ ! -d django_stack ]; then \
		git clone git@github.com:freedomofpress/django_stack.git; \
	fi

pip: devops/venv
	. ./venv/bin/activate; \
	pip install -r django_stack/requirements.txt

devops/venv: clone
	virtualenv venv

molecule: galaxy
	. ./venv/bin/activate && molecule create; \
	molecule converge

galaxy: pip
	ansible-galaxy install -r requirements.yml

syncdjango:
	. ./venv/bin/activate && molecule converge --tags django

destroy:
	. ./venv/bin/activate && molecule destroy
