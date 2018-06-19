import subprocess


docker_id = subprocess.check_output(["docker-compose",
                                     "ps",
                                     "-q",
                                     "django"]).rstrip()
testinfra_hosts = ["docker://{}".format(docker_id.decode('utf-8'))]


def test_ensure_gunicorn_file(host):
    """ Check to ensure gunicorn.py in place"""

    gunicorn_config = host.file("/etc/gunicorn/gunicorn.py")
    assert gunicorn_config.exists
