.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}
UID := $(shell id -u)

.PHONY: ci-go
ci-go: ## Provisions and tests a prod-like setup.
	./scripts/ci-runner.sh

.PHONY: flake8
flake8: ## Runs flake8 on source.
	flake8 api blog home pledges search securethenews sites --exclude 'migrations/'

.PHONY: dev-createdevdata
dev-createdevdata: ## Imports site data in dev environment.
	docker-compose exec stn_django bash -c "./manage.py migrate"
	docker-compose exec stn_django bash -c "./manage.py createdevdata"

.PHONY: dev-makemigrations
dev-migrate: ## Generates new db migrations and applies them.
	docker-compose exec stn_django bash -c "./manage.py makemigrations"
	docker-compose exec stn_django bash -c "./manage.py migrate"

.PHONY: dev-scan
dev-scan: ## Rescans all websites in dev environment.
	docker-compose exec stn_django bash -c "./manage.py scan"

.PHONY: dev-chownroot
dev-chownroot: ## Fixes root-owner permissions created by docker.
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: update-pip-dependencies
update-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR)/securethenews:/code" -it quay.io/freedomofpress/ci-python \
		bash -c 'pip install pip-tools && pip-compile \
		--output-file /code/requirements.txt /code/requirements.in'

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
	@for req_file in `find . -type f -name '*requirements.txt'`; do \
		echo "Checking file $$req_file" \
		&& safety check --full-report -r $$req_file \
		&& echo -e '\n' \
		|| exit 1; \
	done

.PHONY: clean
clean: ## Removes temporary gitignored development artifacts
	rm -rvf db.sqlite3 node_modules client/build static

.PHONY: bandit
bandit: ## Runs `bandit` static code analysis tool for security bugs
	bandit --recursive . -lll --exclude molecule,node_modules,.venv

.PHONY: build-prod-container
build-prod-container: ## Builds a django container for intended production usage
	docker build -f docker/ProdDockerfile -t quay.io/freedomofpress/securethe.news .

.PHONY: run-prod-env
run-prod-env: ## Runs prod-like env (run build-prod-container first)
	@DJANGO_ENV_FILE=./docker/ci.env HOST_GUNICORN_DIR=./docker/gunicorn docker-compose -f ci-docker-compose.yaml up -d

.PHONY: dev-go
dev-go: dev-build ## Runs development environment
	docker-compose up

.PHONY: dev-build
dev-build: ## Build development environment contaners
	echo UID=$(UID) > .env && docker-compose build

.PHONY: app-tests
app-tests: ## Run development tests (works against prod or dev env)
	docker-compose run stn_django ./manage.py test --noinput --keepdb

.PHONY: ops-tests
ops-tests: ## Run testinfra-based tests (functional)
	pytest --junit-xml test-results/ops-tests.xml infratests

# Explaination of the below shell command should it ever break.
# 1. Set the field separator to ": ##" to parse lines for make targets.
# 2. Check for second field matching, skip otherwise.
# 3. Print fields 1 and 2 with colorized output.
# 4. Sort the list of make targets alphabetically
# 5. Format columns with colon as delimiter.
.PHONY: help
help: ## Prints this message and exits.
	@printf "Makefile for developing and testing Secure The News.\n"
	@printf "Subcommands:\n\n"
	@perl -F':\s+##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t
