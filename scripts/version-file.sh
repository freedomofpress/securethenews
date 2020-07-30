#!/bin/bash
#
#
#
# Write deployment version information to a file on disk

set -e

DEPLOY_FILE="${DJANGO_VERSION_FILE:-/deploy/version}"

cat /dev/null > "${DEPLOY_FILE}"

echo -e "## GIT INFO #####\n" >> "${DEPLOY_FILE}"

git_branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo "N/A")"
echo -e "git branch: ${git_branch}\n" >> "${DEPLOY_FILE}"

case "$git_branch" in
    N/A)
        echo -e "release: $(git describe --exact-match)" >> "${DEPLOY_FILE}";;
    prod)
        echo -e "release: $(git describe HEAD^2)" >> "${DEPLOY_FILE}";;
    *)
        echo -e "last release and commits since: $(git describe)" >> "${DEPLOY_FILE}";;
esac

echo >> "${DEPLOY_FILE}"
git log -5 --oneline >> "${DEPLOY_FILE}"

echo -e "\n## PYTHON INFO #####" >> "${DEPLOY_FILE}"
python --version >> "${DEPLOY_FILE}"

echo -e "\n## PYTHON DEPS #####" >> "${DEPLOY_FILE}"
pip freeze >> "${DEPLOY_FILE}"

echo -e "\n## SYS INFO #####" >> "${DEPLOY_FILE}"
cat /etc/*-release >> "${DEPLOY_FILE}"
