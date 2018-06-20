import json
import subprocess


docker_id = subprocess.check_output(["docker-compose",
                                     "ps",
                                     "-q",
                                     "django"]).rstrip()
testinfra_hosts = ["docker://{}".format(docker_id.decode('utf-8'))]


def request_and_scrape(url, filter_key, host):
    """ Take in URL, grab the relevant log line,
        return dict for comparison """

    JSON_LOG_FILE = "/django-logs/app.log"
    # Generate log event via http requests
    host.run("curl -L --user-agent testinfra --header 'Host: app'"
             " http://localhost:8000" + url)
    # Pick out the last log line from django logs
    # This is obviously only reliable test on a test instance with no
    # other incoming traffic.
    grab_log = host.check_output("/bin/grep {0} {1} | tail -n 1".format(
        filter_key,
        JSON_LOG_FILE
    ))

    # Process JSON
    raw_json = json.loads(grab_log)[filter_key]
    # The current json structure uses the time as the key
    # its a pretty dumb design.
    filtered_json = raw_json[list(raw_json)[0]]

    return filtered_json


def test_json_log_exception(host):
    """
    Ensure json logging is working for exception
    """

    url = "/page-doesnt-exist/"

    request = {
        "data": {},
        "meta": {
            "http_host": "app",
            "http_user_agent": "testinfra",
            "path_info": url,
            "remote_addr": "127.0.0.1"
        },
        "method": "GET",
        "path": url,
        "scheme": "http",
        "user": "AnonymousUser"
    }

    error_line = request_and_scrape(url, 'ERROR', host)
    assert 'exception' in error_line
    assert error_line['request'] == request


def test_json_log_200(host):
    """
    Ensure json logging is working for requests
    """

    should_return = {"request":
                     {"data": {},
                         "meta": {"http_host": "app",
                                  "http_user_agent": "testinfra",
                                  "path_info": "/",
                                  "remote_addr": "127.0.0.1"},
                      "method": "GET",
                      "path": "/",
                      "scheme": "http",
                      "user": "AnonymousUser"},
                     "response": {
                         "charset": "utf-8",
                         "headers": {
                             "Content-Type": "text/html; charset=utf-8"
                         },
                         "reason": "OK",
                         "status": 200}}

    assert request_and_scrape('/', 'INFO', host) == should_return


def test_dl_logger_doesnt_propogate(host):
    """
    Ensure dl_logger events aren't being dumped into django logs. This is a
    problem of our catch all behavior and checks to make sure we have the
    django logging module with propogate disabled

    ex: {"asctime": "______", "levelname": "WARNING", "name": "dl_logger",
        "module": "middleware",
        "message": "<django_logging.log_object.LogObject object
                    at 0x3aa51603be0>"}
    """
    host.run("curl -L --user-agent testinfra --header 'Host: app'"
             " http://localhost:8000/")

    grep_pattern = '\"dl_logger\"'
    dl_logger_grep = host.run("egrep -q -r {}  /django-logs".format(
                    grep_pattern))

    assert dl_logger_grep.rc != 0
