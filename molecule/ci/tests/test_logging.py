import json
import pytest

def request_and_scrape(url, filter_key, host):
    """ Take in URL, grab the relevant log line,
        return dict for comparison """

    JSON_LOG_FILE = "/var/www/django-alpha/logs/app.log"
    # Generate log event via http requests
    host.run("curl --user-agent testinfra http://localhost:8000" + url)
    # Pick out the last log line from django logs
    # This is obviously only reliable test on a test instance with no
    # other incoming traffic.
    grab_log = host.check_output("grep {0} {1} | tail -n 1".format(
                                    filter_key,
                                    JSON_LOG_FILE
                                    ))
    # Process JSON
    raw_json = json.loads(grab_log)[filter_key]
    # The current json structure uses the time as the key
    # its a pretty dumb design.
    filtered_json = raw_json[raw_json.keys()[0]]

    return filtered_json


def test_json_log_exception(host):
    """
    Ensure json logging is working for exception
    """

    url = "/page-doesnt-exist/"

    request = {
                "data": {},
                "meta": {
                    "http_host": "localhost:8000",
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
                             "meta": {"http_host": "localhost:8000",
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

    assert request_and_scrape('/','INFO', host) == should_return
