# Secure the News

## Getting Started with Vagrant

We assume you have Vagrant (>=1.8.4) and Ansible (>=1.9.4) installed.

```sh
$ vagrant up
$ vagrant ssh
# in the VM
$ cd /vagrant/securethenews
$ python3 manage.py runserver 0.0.0.0:8000
```

### Notes

* Port 8000 is forwarded from the guest to the host. By default, `runserver`
  runs on `127.0.0.1`, so you need to specify `0.0.0.0` for the port forwarding
  to work.
* We are working with Python 3, but Python 2 is the default Python on Ubuntu
  14.04, which is the platform we are using for the development VM for now.
  Therefore, you will need to specify `python3 manage.py` instead of
  `./manage.py` which you may be used to.
