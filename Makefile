.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}

.PHONY: ci-go
ci-go: ## Provisions and tests a prod-like setup.
	@molecule test -s ci

.PHONY: ci-tests
ci-tests: ## Runs test suite against prod-like setup.
	@molecule verify -s ci

.PHONY: flake8
flake8: ## Runs flake8 on source.
	flake8 api blog home pledges search securethenews sites --exclude 'migrations/'

.PHONY: dev-go
dev-go: ## Creates dev environment.
	molecule converge -s dev

.PHONY: dev-createdevdata
dev-createdevdata: ## Imports site data in dev environment.
	docker exec -it stn_django bash -c "./manage.py migrate"
	docker exec -it stn_django bash -c "./manage.py createdevdata"

.PHONY: dev-makemigrations
dev-migrate: ## Generates new db migrations and applies them.
	docker exec -it stn_django bash -c "./manage.py makemigrations"
	docker exec -it stn_django bash -c "./manage.py migrate"

.PHONY: dev-scan
dev-scan: ## Rescans all websites in dev environment.
	docker exec -it stn_django bash -c "./manage.py scan"

.PHONY: dev-chownroot
dev-chownroot: ## Fixes root-owner permissions created by docker.
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: dev-killapp
dev-killapp: ## Destroys dev environment.
	molecule destroy -s dev

.PHONY: update-pip-dependencies
update-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -it quay.io/freedomofpress/ci-python \
		bash -c 'pip install pip-tools && pip-compile \
		--output-file /code/requirements.txt /code/requirements.in'

# Update dev/testing Python dependencies.
	pip-compile --output-file molecule/requirements.txt molecule/requirements.in

.PHONY: dev-debug
dev-debug: ## Creates local docker container to troubleshoot dev env.
	docker build -t stn_django -f molecule/dev/DjangoDockerfile .
	docker run -v $(DIR):/django -it stn_django bash
	
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
