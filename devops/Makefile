all: molecule

pip: venv
	. ./venv/bin/activate; \
	pip install -r django_stack/requirements.txt

venv:
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
