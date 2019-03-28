.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}
UID := $(shell id -u)
GIT_REV := $(shell git rev-parse HEAD | cut -c1-10)

.PHONY: ci-go
ci-go: ## Provisions and tests a prod-like setup.
	./scripts/ci-runner.sh

.PHONY: lint
lint: ## Runs linters
	flake8

.PHONY: dev-createdevdata
dev-createdevdata: ## Imports site data in dev environment.
	docker-compose exec django bash -c "./manage.py migrate"
	docker-compose exec django bash -c "./manage.py createdevdata"

.PHONY: dev-makemigrations
dev-migrate: ## Generates new db migrations and applies them.
	docker-compose exec django bash -c "./manage.py makemigrations"
	docker-compose exec django bash -c "./manage.py migrate"

.PHONY: dev-scan
dev-scan: ## Rescans all websites in dev environment.
	docker-compose exec django bash -c "./manage.py scan"

.PHONY: dev-chownroot
dev-chownroot: ## Fixes root-owner permissions created by docker.
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: update-pip-dependencies
update-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR)/securethenews:/code" -it python:3.6-slim \
		bash -c 'pip install pip-tools && apt-get update && apt-get install git -y && pip-compile \
		--output-file /code/requirements.txt /code/requirements.in'

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
	@for req_file in `find . -type f -name '*requirements.txt'`; do \
		echo "Checking file $$req_file" \
		&& safety check --ignore 36351 --ignore 36546 --ignore 36533 --ignore 36534\
		--ignore 36541 --full-report -r $$req_file \
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
build-prod-container: prod-concat-docker ## Builds prod environment
	docker-compose -f ci-docker-compose.yaml build --no-cache

.PHONY: run-prod-env
run-prod-env: ## Runs prod-like env (run build-prod-container first)
	docker-compose -f ci-docker-compose.yaml up -d

.PHONY: prod-push
prod-push: ## Publishes prod container image to registry
	docker tag quay.io/freedomofpress/securethenews:latest quay.io/freedomofpress/securethenews:$(GIT_REV)
	docker push quay.io/freedomofpress/securethenews
	docker push quay.io/freedomofpress/securethenews:$(GIT_REV)

.PHONY: staging-push
staging-push: ## Publishes prod container image to registry with staging tag
	docker tag quay.io/freedomofpress/securethenews:latest quay.io/freedomofpress/securethenews:staging
	docker tag quay.io/freedomofpress/securethenews:latest quay.io/freedomofpress/securethenews:$(GIT_REV)
	docker push quay.io/freedomofpress/securethenews:staging
	docker push quay.io/freedomofpress/securethenews:$(GIT_REV)

.PHONY: dev-go
dev-go: dev-init ## Runs development environment
	docker-compose up

.PHONY: dev-init
dev-init: dev-concat-docker docker-env-inject ## Build development environment contaners
	docker-compose build

.PHONY: docker-env-inject
docker-env-inject: ## Layout UID value for docker-compose ingestion
	echo DJANGO_ENV_FILE=./docker/ci.env > .env
	echo HOST_GUNICORN_DIR=./docker/gunicorn >> .env
	echo UID=$(UID) >> .env

.PHONY: dev-concat-docker
dev-concat-docker: ## Concat docker files in prep for dev env
	cd docker && cat djangodocker.snippet dev-django djangodocker-runcmds.snippet > DevDjangoDockerfile

.PHONY: prod-concat-docker
prod-concat-docker: docker-env-inject ## Concat docker files in prep for prod env
	cd docker && cat 1-prod-node djangodocker.snippet 2-prod-django djangodocker-runcmds.snippet > ProdDjangoDockerfile

.PHONY: app-tests-dev
app-tests-dev: ## Run development tests (dev)
	docker-compose run django ./manage.py test --noinput --keepdb

.PHONY: app-tests-prod
app-tests-prod: ## Run development tests (prod)
	docker-compose -f ci-docker-compose.yaml run django ./manage.py test --noinput --keepdb

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
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t
