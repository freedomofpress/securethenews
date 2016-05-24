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
