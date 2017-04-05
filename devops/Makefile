all: molecule

pip: venv
	. ./venv/bin/activate; \
	pip install -r roles/freedomofpress.djang_stack/requirements.txt

venv: galaxy
	virtualenv venv

molecule: pip
	. ./venv/bin/activate && molecule create; \
	molecule converge

galaxy:
	ansible-galaxy install -r requirements.yml

syncdjango:
	. ./venv/bin/activate && molecule converge --tags django

destroy:
	. ./venv/bin/activate && molecule destroy

login:
	. ./venv/bin/activate && molecule login
