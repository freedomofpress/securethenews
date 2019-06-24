#!/bin/bash
#
#
#
# Write deployment version information to a file on disk

set -e

DEPLOY_FILE="${DJANGO_VERSION_FILE:-/deploy/version}"

cat /dev/null > "${DEPLOY_FILE}"

echo -e "## GIT INFO #####\n" >> "${DEPLOY_FILE}"
git log -5 --oneline >> "${DEPLOY_FILE}"

echo -e "\n## PYTHON INFO #####" >> "${DEPLOY_FILE}"
python --version >> "${DEPLOY_FILE}"

echo -e "\n## PYTHON DEPS #####" >> "${DEPLOY_FILE}"
pip freeze >> "${DEPLOY_FILE}"

echo -e "\n## SYS INFO #####" >> "${DEPLOY_FILE}"
cat /etc/*-release >> "${DEPLOY_FILE}"
