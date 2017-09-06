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

.PHONY: dev-go
dev-go: ## Creates dev environment.
	molecule converge -s dev

.PHONY: dev-createdevdata
dev-createdevdata: ## Imports site data in dev environment.
	docker exec -it stn_django bash -c "./manage.py migrate"
	docker exec -it stn_django bash -c "./manage.py createdevdata"

.PHONY: dev-scan
dev-scan: ## Rescans all websites in dev environment.
	docker exec -it stn_django bash -c "./manage.py scan"

.PHONY: dev-chownroot
dev-chownroot: ## Fixes root-owner permissions created by docker.
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: dev-killapp
dev-killapp: ## Destroys dev environment.
	molecule destroy -s dev

.PHONY: dev-debug
dev-debug: ## Creates local docker container to troubleshoot dev env.
	docker build -t stn_django -f molecule/dev/DjangoDockerfile .
	docker run -v $(DIR):/django -it stn_django bash
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
