import subprocess


docker_id = subprocess.check_output(["docker-compose",
                                     "ps",
                                     "-q",
                                     "django"]).rstrip()
testinfra_hosts = ["docker://{}".format(docker_id.decode('utf-8'))]
