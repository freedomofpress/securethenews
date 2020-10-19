#!/usr/bin/env python
import json
import traceback
import glob
import subprocess
import sys
import pathlib


def check_full_report(ids_to_ignore=[]):
    """Runs `safety` on all requirements files, outputs the full report
    for each.  Exits with a success code (0) if all the checks also
    executed with success, and exits with a failure code (1)
    otherwise.  Intended to be run in a CI context where the exit code
    of this command alone determines the pass/fail status of the
    overall check.

    """
    success = True
    command = ['safety', 'check', '--full-report']
    for ignored_id in ids_to_ignore:
        command.extend(['-i', ignored_id])
    for filename in glob.glob('**/*requirements.txt', recursive=True):
        print('Checking {}'.format(filename))
        result = subprocess.run(command + ['-r', filename])
        if result.returncode != 0:
            success = False
    return 0 if success else 1


if __name__ == '__main__':
    project_path = pathlib.Path(__file__).parent.parent / "project.json"

    project = json.loads(project_path.read_text())

    try:
        sys.exit(
            check_full_report(project['variables']['SAFETY_IGNORE_IDS'])
        )
    except Exception:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
