#!/usr/bin/env bash
#
# Release the project and bump version number in the process.

set -e

cd "$(dirname "$0")"

FORCE=false

usage() {
    echo "Usage: $0 [options] VERSION"
    echo
    echo "VERSION:"
    echo "  major: bump major version number"
    echo "  minor: bump minor version number"
    echo "  patch: bump patch version number"
    echo
    echo "Options:"
    echo "  -f, --force:  force release"
    echo "  -h, --help:   show this help message"
    exit 1
}

# parse args
while [ "$#" -gt 0 ]; do
    case "$1" in
    -f | --force)
        FORCE=true
        shift
        ;;
    -h | --help)
        usage
        ;;
    *)
        break
        ;;
    esac
done

# check if version is specified
if [ "$#" -ne 1 ]; then
    usage
fi

if [ "$1" != "major" ] && [ "$1" != "minor" ] && [ "$1" != "patch" ]; then
    usage
fi

# check if git is clean and force is not enabled
if ! git diff-index --quiet HEAD -- && [ "$FORCE" = false ]; then
    echo "Error: git is not clean. Please commit all changes first."
    exit 1
fi

# releases must come from main, in sync with origin
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" != "main" ]; then
    echo "Error: releases must be cut from main (currently on '$branch')."
    exit 1
fi

git fetch origin main --tags --quiet
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "Error: local main is not in sync with origin/main. Run 'git pull --ff-only' first."
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "Error: gh is not installed. Please install the GitHub CLI from https://cli.github.com/"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv from https://docs.astral.sh/uv/"
    exit 1
fi

echo "Would bump version:"
uv version --bump "$1" --dry-run

# prompt for confirmation
if [ "$FORCE" = false ]; then
    read -p "Do you want to release? [yY] " -n 1 -r
    echo
else
    REPLY="y"
fi
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # replace version number
    uv version --bump "$1"

    new_version=$(uv version --short)

    # commit changes
    git add pyproject.toml uv.lock
    git commit -m "bump version to $new_version"
    git tag -a "v$new_version" -m "v$new_version"

    # push changes
    git push origin main
    git push origin "v$new_version"

    # publish the GitHub release (triggers .github/workflows/release.yml -> PyPI)
    gh release create "v$new_version" --title "v$new_version" --generate-notes
else
    echo "Aborted."
    exit 1
fi
