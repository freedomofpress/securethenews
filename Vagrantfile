# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.define "securethenews" do |securethenews|
    securethenews.vm.box = "debian/contrib-jessie64"
    securethenews.vm.hostname = "securethenews"

    securethenews.vm.network "forwarded_port", guest: 8000, host: 8000
    securethenews.vm.network "forwarded_port", guest: 35729, host: 35729 # livereload

    securethenews.vm.provider "virtualbox" do |vb|
      # Building nodejs packages triggers the OOM killer with 512MB of RAM.
      vb.memory = 1024
    end

    securethenews.vm.provider "libvirt" do |lv|
      lv.memory = 1024
    end

    securethenews.vm.provider "docker" do |d, override|
      d.build_dir = 'docker'
      d.has_ssh = true

      # Avoid error caused by defining vm.box for the Docker provider
      override.vm.box = nil
    end

    securethenews.vm.provision "ansible" do |ansible|
      ansible.playbook = "ansible/playbook.yml"
    end
  end
end
