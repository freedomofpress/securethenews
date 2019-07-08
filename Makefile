.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}
UID := $(shell id -u)
GIT_REV := $(shell git rev-parse HEAD | cut -c1-10)
GIT_BR := $(shell git rev-parse --abbrev-ref HEAD)
STN_IMAGE := quay.io/freedomofpress/securethenews

.PHONY: ci-go
ci-go: ## Provisions and tests a prod-like setup.
	cp .env.prod .env
	./scripts/ci-runner.sh

.PHONY: lint
lint: ## Runs linters
	flake8

.PHONY: check-migrations
check-migrations: ## Check for ungenerated migrations
	docker-compose exec -T django bash -c "./manage.py makemigrations --dry-run --check"

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
		--output-file /code/requirements.txt /code/requirements.in && \
        pip-compile -U --no-header --output-file /code/dev-requirements.txt /code/dev-requirements.in'

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
build-prod-container:
	cp ./.env.prod ./.enva
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
	cp ./.env.develop ./.env

.PHONY: app-tests-dev
app-tests-dev: ## Run development tests (dev)
	docker-compose run django ./manage.py test --noinput --keepdb

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
