# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  # domain-scan's Dockerfile specifies Ubuntu 14.04.4, so let's try that first.
  # I'm new to Docker, so I don't know if it's important for the FROM of the
  # dockerfile and the host machine to match in some way. I'm pretty sure they
  # don't have to match, but for now...
  config.vm.box = "ubuntu/trusty64"

  # In the interest of iterating quickly, will use the shell provisioner to
  # start. This should be converted to something more sophisticated (e.g.
  # Ansible) eventually.
  config.vm.provision "shell", path: "provision.sh"

  config.vm.provider "virtualbox" do |v|
    # domain-scan depends on lxml, but installing lxml requires building a
    # native library which in turn requires > 512MB of RAM; otherwise, gcc exits
    # with an internal compiler error: http://stackoverflow.com/a/25916353.
    v.memory = 1024
  end

end
