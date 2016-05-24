# Secure the News

**Warning: currently very early work in progress**

First things first, let's set up a Vagrantfile for testing and development. I
anticipate that this machine will host:

1. The web frontend
2. The automated scanning tool
3. The database of results from the automated scans
4. A Docker container of domain-scan that is used to perform the automated scans.
   * Since domain-scan has so many dependencies, I'm inclined to just use the
     provided Docker environment and see how far that gets us, rather than
     trying to install it alongside everything else on the main server.

## Getting Started

We're using Vagrant for the development environment. I assume you have Vagrant
installed, are familiar with the basics of using it, etc. For now, all you need
to do is:

    vagrant up

The VM has domain-scan cloned and the docker containers built. To scan domains,
see the instructions in the domain-scan README for
[working with the Docker container](https://github.com/18F/domain-scan#using-with-docker).
