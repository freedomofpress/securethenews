# Declare subcommands as "phony" targets, since they're not directories.
.PHONY: ansible dev help

ansible:
	ansible-galaxy install -r ansible/requirements.yml -p ansible/roles

dev:
	make ansible
	vagrant up --provision

help:
	@echo Makefile for SecureTheNews
	@echo Subcommands:
	@echo "\t ansible: Fetch dependencies for Ansible roles."
	@echo "\t dev: Creates a Vagrant VM for local development."

