import subprocess


docker_id = subprocess.check_output(["docker-compose",
                                     "ps",
                                     "-q",
                                     "django"]).rstrip()
testinfra_hosts = ["docker://{}".format(docker_id.decode('utf-8'))]

SKIP_LOG_TEST_MSG = "circle back and test this from container stdout"

@pytest.mark.skip(reason=SKIP_LOG_TEST_MSG)
def test_ensure_gunicorn_file(host):
    """ Check to ensure gunicorn.py in place"""

    gunicorn_config = host.file("/etc/gunicorn/gunicorn.py")
    assert gunicorn_config.exists
