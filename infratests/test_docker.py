from .central_docker_find import testinfra_hosts

testinfra_hosts = testinfra_hosts


def test_ensure_gunicorn_file(host):
    """ Check to ensure gunicorn.py in place"""

    gunicorn_config = host.file("/etc/gunicorn/gunicorn.py")
    assert gunicorn_config.exists
