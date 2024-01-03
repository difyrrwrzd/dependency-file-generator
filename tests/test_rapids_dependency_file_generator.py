from unittest import mock

import pytest
import yaml

from rapids_dependency_file_generator.constants import OutputTypes, cli_name
from rapids_dependency_file_generator.rapids_dependency_file_generator import (
    dedupe,
    get_requested_output_types,
    make_dependency_file,
    should_use_specific_entry,
)


def test_dedupe():
    # simple list
    deduped = dedupe(["dep1", "dep1", "dep2"])
    assert deduped == ["dep1", "dep2"]

    # list w/ pip dependencies
    deduped = dedupe(
        [
            "dep1",
            "dep1",
            {"pip": ["pip_dep1", "pip_dep2"]},
            {"pip": ["pip_dep1", "pip_dep2"]},
        ]
    )
    assert deduped == ["dep1", {"pip": ["pip_dep1", "pip_dep2"]}]


@mock.patch(
    "rapids_dependency_file_generator.rapids_dependency_file_generator.os.path.relpath"
)
def test_make_dependency_file(mock_relpath):
    relpath = "../../config_file.yaml"
    mock_relpath.return_value = relpath
    header = f"""\
# This file is generated by `{cli_name}`.
# To make changes, edit {relpath} and run `{cli_name}`.
"""
    env = make_dependency_file(
        file_type="conda",
        name="tmp_env.yaml",
        config_file="config_file",
        output_dir="output_path",
        conda_channels=["rapidsai", "nvidia"],
        dependencies=["dep1", "dep2"],
        extras=None,
    )
    assert env == header + yaml.dump(
        {
            "name": "tmp_env",
            "channels": ["rapidsai", "nvidia"],
            "dependencies": ["dep1", "dep2"],
        }
    )

    env = make_dependency_file(
        file_type="requirements",
        name="tmp_env.txt",
        config_file="config_file",
        output_dir="output_path",
        conda_channels=["rapidsai", "nvidia"],
        dependencies=["dep1", "dep2"],
        extras=None,
    )
    assert env == header + "dep1\ndep2\n"


def test_should_use_specific_entry():
    # no match
    matrix_combo = {"cuda": "11.5", "arch": "x86_64"}
    specific_entry = {"cuda": "11.6"}
    result = should_use_specific_entry(matrix_combo, specific_entry)
    assert result is False

    # one match
    matrix_combo = {"cuda": "11.5", "arch": "x86_64"}
    specific_entry = {"cuda": "11.5"}
    result = should_use_specific_entry(matrix_combo, specific_entry)
    assert result is True

    # many matches
    matrix_combo = {"cuda": "11.5", "arch": "x86_64", "python": "3.6"}
    specific_entry = {"cuda": "11.5", "arch": "x86_64"}
    result = should_use_specific_entry(matrix_combo, specific_entry)
    assert result is True


def test_get_requested_output_types():
    result = get_requested_output_types(str(OutputTypes.NONE))
    assert result == []

    result = get_requested_output_types([str(OutputTypes.NONE)])
    assert result == []

    result = get_requested_output_types(str(OutputTypes.CONDA))
    assert result == [str(OutputTypes.CONDA)]

    result = get_requested_output_types([str(OutputTypes.CONDA)])
    assert result == [str(OutputTypes.CONDA)]

    result = get_requested_output_types(str(OutputTypes.REQUIREMENTS))
    assert result == [str(OutputTypes.REQUIREMENTS)]

    result = get_requested_output_types([str(OutputTypes.REQUIREMENTS)])
    assert result == [str(OutputTypes.REQUIREMENTS)]

    result = get_requested_output_types(
        [str(OutputTypes.REQUIREMENTS), str(OutputTypes.CONDA)]
    )
    assert result == [str(OutputTypes.REQUIREMENTS), str(OutputTypes.CONDA)]

    with pytest.raises(ValueError):
        get_requested_output_types("invalid_value")

    with pytest.raises(ValueError):
        get_requested_output_types(["invalid_value"])

    with pytest.raises(ValueError):
        get_requested_output_types([str(OutputTypes.NONE), str(OutputTypes.CONDA)])
