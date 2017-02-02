# Secure the News

## Getting Started with the Development Environment

Make sure you have Vagrant (>=1.8.5), Ansible (>=2.0), and either VirtualBox or
[Docker](https://docs.docker.com/engine/installation/)
installed. A Makefile is provided to automate the setup of the development
environment.

First, set the environmental variable `VAGRANT_DEFAULT_PROVIDER` to `docker`
or `virtualbox` to specify the provider. If you're on Qubes, use `docker`, else
you can select either (as long as it's installed).

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


    $ python3 manage.py dumpdata sites.{Site,Scan} > sites/fixtures/dev.json

### Live reload

The default gulp `watch` task uses `gulp-livereload` to automatically trigger a
browser refresh when changes to the frontend code are detected. In order to take
advantage of this, you will need to install the [LiveReload Chrome
extension](https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei?hl=en).

Once you've installed the extension, simply load the development site in your
browser (`localhost:8000`) and click the LiveReload extension icon to initiate
live reloading.

## Notes

* Port 8000 is forwarded from the guest to the host. By default, `runserver`
  runs on `127.0.0.1`, so you need to specify `0.0.0.0` for the port forwarding
  to work.
* We are working with Python 3, but Python 2 is the default Python on Ubuntu
  14.04, which is the platform we are using for the development VM for now.
  Therefore, you will need to specify `python3 manage.py` instead of
  `./manage.py` which you may be used to.
