# Secure the News

## Getting Started with the Development Environment

Make sure you have Vagrant (>=1.8.5) and Ansible (>=2.0) installed. A
Makefile is provided to automate the setup of the development
environment. Run:

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
migrations". To apply the migrations, run `python3 manage.py migrate`.

Once you've successfully set up your new development environment, you should
continue to the next section to load the development fixtures.

### Development fixtures

To encourage rapid development, the repository includes database fixtures that
can be used to automatically populate the development database.

The fixtures include:

- ContentPages from the initial site design ("About", "How", "Why?")
- A BlogIndexPage and some test BlogPosts.
- An initial set of Sites based on `prototype_data/domains.csv`, with the
  results of a single scan generated with `python3 manage.py scan`.
- A default superuser that you can use to log in to the Admin Interface
  (username: **admin**, password: **admin**).

To load the fixtures:

    $ cd /vagrant/securethenews # in the VM
    # Make sure you've applied all of the migrations first
    $ python3 manage.py migrate
    $ python3 manage.py loaddata fixtures/dev.json

If you want to update the fixtures, use the following command (and make sure you
update the description of their contents in this README):

    $ python3 manage.py dumpdata --natural-primary --natural-foreign --exclude contenttypes --exclude auth.Permission --exclude sessions --indent 4 > fixtures/dev.json

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
