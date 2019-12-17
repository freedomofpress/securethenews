# Secure the News

[![CircleCI](https://circleci.com/gh/freedomofpress/securethenews.svg?style=svg)](https://circleci.com/gh/freedomofpress/securethenews)

## Getting Started with the Development Environment

The installation instructions below assume you have the following software on your machine:

* [pipenv](https://docs.pipenv.org/#install-pipenv-today)
* [docker](https://docs.docker.com/engine/installation/)

From the checkout directory, run the following to jump into a virtualenv:

```bash
# The very first time run
$ pipenv install
# Each subsequent time run this to enter a virtualenv shell
$ pipenv shell
```

Then run the following, which will be need to be run once at clone of this repo:

```bash
make dev-init
```

To start up the development environment you can use the normal `docker-compose` flow:

```bash
docker-compose up
```

If this command completes successfully, your development site will be available
at: http://localhost:8000

To import the example data, run:

```bash
docker-compose exec django ./manage.py createdevdata
```

This will also create an admin user for the web interface at
http://localhost:8000/admin/ (username: test, password: test).

If you want to start the TLS scan for all the news sites in your development
environment, run:

```bash
make dev-scan
```

For a full list of all helper commands in the Makefile, run `make help`. And,
of course, you can obtain a shell directly into any of the containers using `docker-compose` syntax. Just keep in mind the default shell is `ash` under alpine. Here is an example of entering the django container:

```bash
$ docker-compose exec django ash
```

### Debugging

If you want to use the [PDB](https://docs.python.org/3/library/pdb.html) program for debugging, it is possible.  First, add this line to an area of the code you wish to debug:

```
import ipdb; ipdb.set_trace()
```

Second, attach to the running Django container.  This must be done in a shell, and it is within this attached shell that you will be able to interact with the debugger.  The command to attach is `docker attach <ID_OF_DJANGO_CONTAINER>`, and on UNIX-type systems, you can look up the ID and attach to the container with this single command:

```
docker attach $(docker-compose ps -q django)
```

Once you have done this, you can load the page that will run the code with your `import ipdb` and the debugger will activate in the shell you attached. To detach from the shell without stopping the container press `Control+P` followed by `Control+Q`.

## Getting Started with the Production Environment

The environment is fairly similar to development with the exception that your code will not auto-reload and be reflected in the container. So this is not a great environment to development under but it reflects a production-like environment run under `gunicorn` and behind a reverse-proxy nginx server.

The flow is this:

```bash
# Build the prod container (everytime you make a code-change need to re-do this)
make build-prod-container

# Run the prod environment
docker-compose -f prod-docker-compose.yaml up

# Run production apptests
make app-tests-prod

# Run ops tests
make ops-tests

# Teardown prod
docker-compose -f prod-docker-compose.yaml down
```


### Dependency Management

#### Adding new requirements

New requirements should be added to `*requirements.in` files, for use with `pip-compile`.
There are two Python requirements files:

* `requirements.in` production application dependencies
* `dev-requirements.in` local testing and CI requirements

Add the desired dependency to the appropriate `.in` file, then run:

```
$ make compile-pip-dependencies
```

All requirements files will be regenerated based on compatible versions. Multiple `.in`
files can be merged into a single `.txt` file, for use with `pip`. The Makefile
target handles the merging of multiple files.

This process is the same if a requirement needs to be changed (i.e. its version number restricted) or removed.  Make the appropriate change in the correct `requirements.in` file, then run the above command to compile the dependencies.

#### Upgrading existing requirements

There are separate commands to upgrade a package without changing the `requirements.in` files.  The command

```
$ make upgrade-pip PACKAGE=package-name
```

will update the package named `package-name` to the latest version allowed by the constraints in `requirements.in` and compile a new `dev-requirements.txt` and `requirements.txt` based on that version.

If the package appears only in `dev-requirements.in`, then you must use this command:

```
$ make upgrade-pip-dev PACKAGE=package-name
```

which will update the package named `package-name` to the latest version allowed by the constraints in `requirements.in` and compile a new `dev-requirements.txt`.

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
