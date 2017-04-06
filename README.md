# Secure the News

[![Build Status](https://travis-ci.org/freedomofpress/securethenews.svg?branch=master)](https://travis-ci.org/freedomofpress/securethenews)

## Getting Started with the Development Environment

Make sure you have Vagrant (>=1.8.5), Ansible (>=2.0), and either VirtualBox or
[Docker](https://docs.docker.com/engine/installation/)
installed. A Makefile is provided to automate the setup of the development
environment.

By [default](https://www.vagrantup.com/docs/providers/default.html), Vagrant
will use the `virtualbox` provider. The Vagrantfile currently also supports the
`libvirt` and `docker` providers. The Docker provider is useful on host
platforms such as Qubes, which do not support virtualized providers. If you
want to use a non-default provider, set the environment variable
`VAGRANT_DEFAULT_PROVIDER` to `docker` or `libvirt`. Alternatively you may pass
the `--provider` flag to Vagrant, but it's easier to set the environment
variable.

Then run:

    $ make dev
    $ vagrant ssh

The interactive session will automatically launch a tmux environment designed
for developers working on Secure the News. There are 3 panes:

1. A shell for interactive work.
2. The Django development web server. If you quit the web server, you can start
   it again with: `python3 manage.py runserver 0.0.0.0:8000`. The development
   server will live reload whenever it detects changes to the source files.
3. gulp, to build frontend assets (CSS and JS). gulp is setup to live reload
   whenever it detects changes to the source files.

If this is your first login after creating the virtual development environment,
you will notice the development web server warning you about "unapplied
migrations". To set up the development environment, run:

    $ python3 manage.py migrate
    $ python3 manage.py createdevdata

`createdevdata` creates a default superuser (username: `test`, password:
`test`) that you can use to log in to the Admin interface at `/admin`.

### Development Fixtures

The `createdevdata` management commands loads Site and Scan data from the
fixtures in `sites/fixtures/dev.json`. If you change the schema of `sites.Site`
or `sites.Scan`, you will need to update these fixtures, **or future
invocations of `createdevdata` will fail.**

The general process for updating the development fixtures is:

1. Migrate your database to the last migration where the fixtures were updated.
2. Load the fixtures.
3. Run the migrations that you've added.
4. Export the migrated fixtures:

    ```
    $ python3 manage.py dumpdata sites.{Site,Scan} > sites/fixtures/dev.json
    ```

The test suite includes a smoke test for `createdevdata`, so you can easily
verify that the command is working without disrupting your own development
environment.

### Live reload

The default gulp `watch` task uses `gulp-livereload` to automatically trigger a
browser refresh when changes to the frontend code are detected. In order to take
advantage of this, you will need to install the [LiveReload Chrome
extension](https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei?hl=en).

Once you've installed the extension, simply load the development site in your
browser (`localhost:8000`) and click the LiveReload extension icon to initiate
live reloading.

## API

If everything is working correctly, you should be able to find an API endpoint
at `localhost:8000/api` (it will redirect to the current API version).

The API is read-only and can be used to obtain site metadata and the latest scan
for a given site (e.g., `/api/v1/sites` will return a directory, and
`/api/v1/sites/bbc.co.uk` will return details about the BBC). Various filters
and sort options are supported; click the "filters" dialog in the UI to explore
them.

To get all scans for a given site, you can use a path like
`/api/v1/sites/bbc.co.uk/scans`. This URL can also be found in the all_scans
field for a given site result.

If you run a public site, note that read access to the API is available to any
origin via CORS.

The API is implemented using the Django REST framework; documentation for it can
be found here:

http://www.django-rest-framework.org/

## Notes

* Port 8000 is forwarded from the guest to the host. By default, `runserver`
  runs on `127.0.0.1`, so you need to specify `0.0.0.0` for the port forwarding
  to work.
* We are working with Python 3, but Python 2 is the default Python on Ubuntu
  14.04, which is the platform we are using for the development VM for now.
  Therefore, you will need to specify `python3 manage.py` instead of
  `./manage.py` which you may be used to.
