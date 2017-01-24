# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 35729, host: 35729 # livereload

  config.vm.define "securethenews" do |securethenews|
    securethenews.vm.hostname = "securethenews"

    securethenews.vm.provider "docker" do |d|
      d.build_dir = 'docker'
      d.has_ssh = true
    end

    securethenews.vm.provider "virtualbox" do |vb|
      config.vm.box = "debian/contrib-jessie64"
      # Building nodejs packages triggers the OOM killer with 512MB of RAM.
      vb.memory = 1024
    end

    securethenews.vm.provider "libvirt" do |lv|
      config.vm.box = "debian/contrib-jessie64"
      lv.memory = 1024
    end

    securethenews.vm.provision "ansible" do |ansible|
      ansible.playbook = "ansible/playbook.yml"
    end
  end
end
