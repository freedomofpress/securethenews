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

### Loading the development fixtures

I have generated fixtures using the sites from `prototype_data/domains.csv` and
a single scan run generated with `python3 manage.py scan`. The fixtures are
stored in the repository and can be quickly loaded into your database so you
have something to work with during development.

To load the fixtures:

```sh
# in the Vagrant VM
$ cd /vagrant/securethenews
$ python3 manage.py loaddata scans/fixtures/0001_20160803T235828.json
```

### Notes

* Port 8000 is forwarded from the guest to the host. By default, `runserver`
  runs on `127.0.0.1`, so you need to specify `0.0.0.0` for the port forwarding
  to work.
* We are working with Python 3, but Python 2 is the default Python on Ubuntu
  14.04, which is the platform we are using for the development VM for now.
  Therefore, you will need to specify `python3 manage.py` instead of
  `./manage.py` which you may be used to.
