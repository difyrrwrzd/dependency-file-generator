#!/bin/bash
# Simple script to update the version string in `_version.py`
set -ue

NEXT_VERSION=$1

sed -i "/__version__/ s/\".*\"/\"${NEXT_VERSION}\"/" src/rapids_dependency_file_generator/_version.py
