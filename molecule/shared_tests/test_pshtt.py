import pytest
import json
import os

PSHTT_CLI_PATH = os.environ['pshtt_location']
PSHTT_DOMAINS = [
    'freedom.press',
    'securedrop.org'
]


def test_pshtt_installed(host):
    """
    We need the pshtt library for the SecureDrop Directory, for querying
    the HTTPS configuration on Landing Pages. The pshtt module recently
    received python3 support, so we install it alongside the other
    webapp pip dependencies, inside a virtualenv

    Therefore we must run the binary from its path on disk within the
    virtualenv. By checking the `--version` output, we can confirm
    that the binary executes OK. Common problems preventing success:

      * lack of PaX flags on Python interpreter (grsecurity only)
      * elasticsearch version conflicts (due to django-json-logging)

    The following checks confirm the above.
    """
    pshtt_binary = host.file(PSHTT_CLI_PATH)
    assert pshtt_binary.exists
    assert host.check_output(pshtt_binary.path + " --version") \
        == "v0.0.1"


@pytest.mark.parametrize('domain', PSHTT_DOMAINS)
def test_pssht_connectivity(host, domain):
    """
    Confirm that the pshtt program can make external network calls,
    otherwise it's useless. Mostly this is to confirm that the pip
    installation pulled in all required dependencies for functionality,
    but also has bearing on confirming the development environment
    works as expected.
    """
    c = host.command("{} -o /tmp/o.csv {}".format(PSHTT_CLI_PATH, domain))
    assert c.rc == 0
    assert c.stderr.strip() == "Wrote results to /tmp/o.csv."


@pytest.mark.parametrize('domain', PSHTT_DOMAINS)
def test_pssht_json_output(host, domain):
    """
    Confirm that the pshtt program reports usable JSON back when asked,
    via the `--json` flag. Perform cursory inspection of the JSON object
    to make sure it's populated correctly.
    """
    c = host.command(PSHTT_CLI_PATH + " --json " + domain)
    assert c.rc == 0
    j = json.loads(c.stdout.strip())
    # JSON output is always a list, so retrieve first item via [0].
    assert j[0]['Live']
    assert j[0]['endpoints']['http']['live']
    assert j[0]['endpoints']['https']['live']
