import glob
import os
import shutil

import pytest

from rapids_dependency_file_generator.rapids_dependency_file_generator import (
    main as dfg,
)

CURRENT_DIR = os.path.dirname(__file__)


@pytest.fixture(scope="session", autouse=True)
def clean_actual_files():
    for root, _, _ in os.walk("tests"):
        if os.path.basename(root) == "actual":
            shutil.rmtree(root)


def make_file_set(file_dir):
    return {
        os.path.relpath(f, file_dir)
        for f in glob.glob(file_dir + "/**", recursive=True)
        if os.path.isfile(f)
    }


def test_integration():
    test_dir = os.path.join(CURRENT_DIR, "examples", "integration")
    expected_dir = os.path.join(test_dir, "output", "expected")
    actual_dir = os.path.join(test_dir, "output", "actual")
    dep_file_path = os.path.join(test_dir, "dependencies.yaml")

    dfg(dep_file_path)

    expected_file_set = make_file_set(expected_dir)
    actual_file_set = make_file_set(actual_dir)

    assert expected_file_set == actual_file_set

    for file in actual_file_set:
        actual_file = open(os.path.join(actual_dir, file)).read()
        expected_file = open(os.path.join(expected_dir, file)).read()
        assert actual_file == expected_file
