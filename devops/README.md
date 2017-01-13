# How-to stand-up a local prod deploy for testing

## Lets do it!
Need the following local requirements:

* `make`
* `python`
* `vagrant`
* `virtualbox`
* `virtualenv`

Hooray! Now perform the following:

* Copy a github private deploy key to `devops/deploy_key`
* From the `devops` directory run `make`

This should setup a vagrant box and run an ansible play against it.
You will then be able to get to a local STN instance @ `https://localhost:4443` in
 a browser. 


## Todo
* Allow optional switching from vbox --> kvm
* Allow work-around to use rsync to copy over current directory (instead of
  using `deploy_key` to reach out to the internetz)
