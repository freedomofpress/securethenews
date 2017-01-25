FROM jesselang/debian-vagrant:jessie

# The containers needs to have Python 2.7 installed in order for the Ansible
# provisioner to work. You might expect jesselang/debian-vagrant to include
# Python by default, since it is based on the official Debian images, but these
# official images use a "minbase" install which does not appear to include
# Python.
RUN apt-get install --no-install-recommends -y python
