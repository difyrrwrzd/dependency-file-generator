import pytest
from unittest import mock
from rapids_dependency_file_generator.rapids_dependency_file_generator import (
    dedupe,
    make_dependency_file,
    should_use_specific_entry,
    get_file_types_to_generate,
)
from rapids_dependency_file_generator.constants import cli_name, GeneratorTypes
import yaml


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
        "conda",
        "tmp_env.yaml",
        "config_file",
        "output_path",
        ["rapidsai", "nvidia"],
        ["dep1", "dep2"],
    )
    assert env == header + yaml.dump(
        {
            "name": "tmp_env",
            "channels": ["rapidsai", "nvidia"],
            "dependencies": ["dep1", "dep2"],
        }
    )

    env = make_dependency_file(
        "requirements",
        "tmp_env.txt",
        "config_file",
        "output_path",
        ["rapidsai", "nvidia"],
        ["dep1", "dep2"],
    )
    assert env == header + "dep1\ndep2\n"


def test_should_use_specific_entry():
    # no match
    matrix_combo = {"cuda": "11.5", "arch": "x86_64"}
    specific_entry = {"cuda": "11.6"}
    result = should_use_specific_entry(matrix_combo, specific_entry)
    assert result == False

    # one match
    matrix_combo = {"cuda": "11.5", "arch": "x86_64"}
    specific_entry = {"cuda": "11.5"}
    result = should_use_specific_entry(matrix_combo, specific_entry)
    assert result == True

    # many matches
    matrix_combo = {"cuda": "11.5", "arch": "x86_64", "python": "3.6"}
    specific_entry = {"cuda": "11.5", "arch": "x86_64"}
    result = should_use_specific_entry(matrix_combo, specific_entry)
    assert result == True


def test_get_file_types_to_generate():
    result = get_file_types_to_generate(str(GeneratorTypes.NONE))
    assert result == []

    result = get_file_types_to_generate([str(GeneratorTypes.NONE)])
    assert result == []

    result = get_file_types_to_generate(str(GeneratorTypes.CONDA))
    assert result == [str(GeneratorTypes.CONDA)]

    result = get_file_types_to_generate([str(GeneratorTypes.CONDA)])
    assert result == [str(GeneratorTypes.CONDA)]

    result = get_file_types_to_generate(str(GeneratorTypes.REQUIREMENTS))
    assert result == [str(GeneratorTypes.REQUIREMENTS)]

    result = get_file_types_to_generate([str(GeneratorTypes.REQUIREMENTS)])
    assert result == [str(GeneratorTypes.REQUIREMENTS)]

    result = get_file_types_to_generate(
        [str(GeneratorTypes.REQUIREMENTS), str(GeneratorTypes.CONDA)]
    )
    assert result == [str(GeneratorTypes.REQUIREMENTS), str(GeneratorTypes.CONDA)]

    with pytest.raises(ValueError):
        get_file_types_to_generate("invalid_value")

    with pytest.raises(ValueError):
        get_file_types_to_generate(["invalid_value"])

    with pytest.raises(ValueError):
        get_file_types_to_generate(
            [str(GeneratorTypes.NONE), str(GeneratorTypes.CONDA)]
        )
