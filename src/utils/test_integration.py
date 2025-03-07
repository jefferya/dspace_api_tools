"""
Test compare_csv module
"""

import pandas

import compare_csv as compare


def test_string_compare():
    """
    Test string_compare
    """
    assert compare.string_compare("a", "a") is True
    assert compare.string_compare("a", "a\n") is False
    assert compare.string_compare("a", "b") is False
    assert compare.string_compare("a", "A") is False
    assert compare.string_compare("a", "a ") is False
    assert compare.string_compare("a", " a") is False
    assert compare.string_compare("a", " a ") is False
    assert compare.string_compare("a", " a\n") is False


def test_string_compare_ignore_whitespace():
    """
    Test string_compare_ignore_whitespace: ignore trailing whitespace
    """
    assert compare.string_compare_ignore_whitespace("a", "a") is True
    assert compare.string_compare_ignore_whitespace("a", "a\n") is True
    assert compare.string_compare_ignore_whitespace("a", "b") is False
    assert compare.string_compare_ignore_whitespace("a", "A") is False
    assert compare.string_compare_ignore_whitespace("a", "a ") is True
    assert compare.string_compare_ignore_whitespace("a", " a") is True
    assert compare.string_compare_ignore_whitespace("a", " a ") is True
    assert compare.string_compare_ignore_whitespace("a", " a\n") is True


def test_input_process_community_valid(tmp_path):
    """
    Test process_input for community with valid data
    """
    comparison_config = compare.community_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_community.csv"
    dspace_input = "src/tests/assets/dspace_community.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    assert output_df["name"][0] == "PASS"
    assert output_df["description"][0] == "PASS"
    assert output_df["abstract"][0] == "PASS"
    assert output_df["dc.title"][0] == "PASS"


def test_input_process_community_differences(tmp_path):
    """
    Test process_input for community with different data
    """
    comparison_config = compare.community_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_community.csv"
    dspace_input = "src/tests/assets/dspace_community_version_2.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    assert output_df["name"][0] == "PASS"
    assert output_df["description"][0] == "FAIL"
    assert output_df["abstract"][0] == "FAIL"
    assert output_df["dc.title"][0] == "FAIL"


def test_input_process_community_missing(tmp_path):
    """
    Test process_input for community with missing rows
    """
    comparison_config = compare.community_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_community.csv"
    dspace_input = "src/tests/assets/dspace_community_empty.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    assert output_df["name"][0] == "FAIL"
    assert output_df["description"][0] == "FAIL"
    assert output_df["abstract"][0] == "FAIL"
    assert output_df["dc.title"][0] == "FAIL"


def test_input_process_collection_valid(tmp_path):
    """
    Test process_input for a collection with different data
    """
    comparison_config = compare.collection_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_collection.csv"
    dspace_input = "src/tests/assets/dspace_collection.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    assert output_df["name"][0] == "PASS"
    assert output_df["description"][0] == "PASS"
    assert output_df["abstract"][0] == "PASS"
    assert output_df["dc.title"][0] == "PASS"


def test_input_process_collection_differences(tmp_path):
    """
    Test process_input for a collection with different data
    """
    comparison_config = compare.collection_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_collection.csv"
    dspace_input = "src/tests/assets/dspace_collection_version_2.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    assert output_df["name"][0] == "PASS"
    assert output_df["description"][0] == "FAIL"
    assert output_df["abstract"][0] == "FAIL"
    assert output_df["dc.title"][0] == "FAIL"


def test_input_process_collection_missing(tmp_path):
    """
    Test process_input for a collection with missing rows
    """
    comparison_config = compare.collection_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_collection.csv"
    dspace_input = "src/tests/assets/dspace_collection_empty.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    assert output_df["name"][0] == "FAIL"
    assert output_df["description"][0] == "FAIL"
    assert output_df["abstract"][0] == "FAIL"
    assert output_df["dc.title"][0] == "FAIL"
