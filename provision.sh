#!/bin/sh
# Mostly based on https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-14-04

set -e

# Update package lists and default installed packages
sudo apt-get update && sudo apt-get upgrade -y

# Put everything in the Vagrant user's home directory, for now
cd /home/vagrant

# Install Docker (for domain-scan)
wget -qO- https://get.docker.com/ | sh
# TODO this didn't work? vagrant isn't in the docker group, I needed to sudo to run docker-compose up
# Theory: Docker's install script somehow made me root :/
sudo usermod -aG docker $(whoami)

# docker-compose depends on pip
sudo apt-get -y install python-pip
sudo pip install docker-compose

# Clone the domain-scan repo
sudo apt-get install -y git
git clone https://github.com/18F/domain-scan.git
cd domain-scan
docker-compose build
