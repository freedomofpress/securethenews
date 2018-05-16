testinfra_hosts = ["local://localhost"]


def test_mainpage(host):
    """
    Basic test to make sure home-page is coming up.
    """

    content = host.check_output("curl -k http://localhost:8080")
    head = host.check_output("curl -I -k http://localhost:8080")
    assert "homepage" in content
    assert "HTTP/1.1 200 OK" in head
