.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}
HOST_UID := $(shell id -u)
GIT_REV := $(shell git rev-parse HEAD | cut -c1-10)
GIT_BR := $(shell git rev-parse --abbrev-ref HEAD)
STN_IMAGE := quay.io/freedomofpress/securethenews
PY_IMAGE := python:3.7-slim

.PHONY: ci-go
ci-go: ## Provisions and tests a prod-like setup.
	./scripts/ci-runner.sh

.PHONY: lint
lint: ## Runs linters
	flake8

.PHONY: check-migrations
check-migrations: ## Check for ungenerated migrations
	docker-compose exec -T django bash -c "./manage.py makemigrations --dry-run --check"

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

.PHONY: compile-pip-dependencies
compile-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code/securethenews -it $(PY_IMAGE) \
		bash -c 'apt-get update && apt-get install gcc libpq-dev -y && \
		pip install pip-tools && \
		pip-compile --generate-hashes --no-header --output-file requirements.txt requirements.in && \
		pip-compile --generate-hashes --no-header --allow-unsafe --output-file dev-requirements.txt dev-requirements.in'

.PHONY: pip-update
pip-update: ## Uses pip-compile to update requirements.txt for upgrading a specific package
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code/securethenews -it $(PY_IMAGE) \
		bash -c 'apt-get update && apt-get install gcc libpq-dev -y && \
		pip install pip-tools && \
		pip-compile --generate-hashes --no-header --upgrade-package $(PACKAGE) --output-file requirements.txt requirements.in && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package $(PACKAGE) --output-file dev-requirements.txt dev-requirements.in'

.PHONY: pip-dev-update
pip-dev-update: ## Uses pip-compile to update dev-requirements.txt for upgrading a specific package
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code/securethenews -it $(PY_IMAGE) \
		bash -c 'apt-get update && apt-get install gcc libpq-dev -y && \
		pip install pip-tools && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package $(PACKAGE) --output-file dev-requirements.txt dev-requirements.in'

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
# Upgrade safety to ensure we are using the latest version.
	pip install --upgrade safety && ./scripts/safety_check.py

.PHONY: clean
clean: ## Removes temporary gitignored development artifacts
	rm -rvf db.sqlite3 node_modules client/build static

.PHONY: bandit
bandit: ## Runs `bandit` static code analysis tool for security bugs
	bandit --recursive . -lll --exclude molecule,node_modules,.venv

.PHONY: build-prod-container
build-prod-container:
	docker-compose -f prod-docker-compose.yaml build --no-cache

.PHONY: run-prod-env
run-prod-env: ## Runs prod-like env (run build-prod-container first)
	docker-compose -f prod-docker-compose.yaml up -d

.PHONY: prod-push
prod-push: ## Publishes prod container image to registry
	docker tag $(STN_IMAGE):latest $(STN_IMAGE):$(GIT_REV)-$(GIT_BR)
	docker push $(STN_IMAGE):latest
	docker push $(STN_IMAGE):$(GIT_REV)-$(GIT_BR)

.PHONY: dev-go
dev-go: dev-init ## Runs development environment
	docker-compose up

.PHONY: dev-init
dev-init: ## pipe ENVs into docker-compose, prevents need of wrapper script
	echo UID=$(HOST_UID) > .env

.PHONY: dev-tests
dev-test: app-tests-dev

.PHONY: app-tests-dev
app-tests-dev: ## Run development tests (dev)
	docker-compose run django /bin/bash -ec \
		"coverage run --source='.' ./manage.py test --noinput --keepdb; \
		coverage html --skip-empty --omit='*/migrations/*.py'; \
		coverage report --fail-under=65 --skip-empty --omit='*/migrations/*.py'"

.PHONY: app-tests-prod
app-tests-prod: ## Run development tests (prod)
	docker-compose -f prod-docker-compose.yaml run django ./manage.py test --noinput --keepdb

.PHONY: npm-audit
npm-audit: ## Checks NodeJS NPM dependencies for vulnerabilities
	@docker-compose run --entrypoint "/bin/ash -c" node 'npm install && $$(npm bin)/npm-audit-plus'

.PHONY: ci-npm-audit
ci-npm-audit:
	@mkdir -p test-results # Creates necessary test-results folder
	@docker-compose run --entrypoint "/bin/ash -c" node 'npm ci && $$(npm bin)/npm-audit-plus --xml > test-results/audit.xml'

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
