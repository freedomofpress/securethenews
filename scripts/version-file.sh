#!/bin/bash
#
#
#
# Write deployment version information to a file on disk

set -e

short_version_out="${DJANGO_SHORT_VERSION_FILE:-/deploy/version-short.txt}"
full_version_out="${DJANGO_FULL_VERSION_FILE:-/deploy/version-full.txt}"

branch="$(git rev-parse --abbrev-ref HEAD)"
commit="$(git rev-parse --short HEAD)"

# prod is special, in that we care what tag was merged in, rather that
# what the merge commit is.
case "$branch" in
    prod)
        branch_desc="on branch: ${branch}"
        ref_desc="release tag: $(git describe HEAD^2)";;
    HEAD)
        branch_desc="no branch, detached HEAD"
        ref_desc="not tagged, $(git describe)";;
    *)
        branch_desc="on branch: ${branch}"
        ref_desc="not tagged, $(git describe)";;
esac

echo "$commit" >"$short_version_out"

cat >"$full_version_out" <<EOF
#### GIT INFO ####

${branch_desc}
commit: ${commit}
${ref_desc}

$(git log -5 --oneline)

#### PYTHON INFO ####

$(python3 --version)

#### PYTHON DEPS ####

$(pip freeze)

#### SYS INFO ####

$(cat /etc/*-release)
EOF
