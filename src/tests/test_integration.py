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
    assert compare.string_compare("", "") is True


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
    assert compare.string_compare_ignore_whitespace("", "") is True
    assert compare.string_compare_ignore_whitespace(float(), float()) is True


def test_member_of_list_compare():
    """
    Test member_of_list_compare
    """
    assert compare.member_of_list_compare(["a", "b", "c"], ["a", "b", "c"]) is True
    assert compare.member_of_list_compare([], []) is True
    assert compare.member_of_list_compare(["a", "b", "c"], ["c", "b", "a"]) is False
    assert compare.member_of_list_compare(["a", "b", "c"], ["a"]) is False
    assert compare.member_of_list_compare(["a", "b", "c"], ["1"]) is False


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


def test_input_process_bitstream_valid(tmp_path):
    """
    Test process_input for a bitstream with valid data and 2 sequences
    """
    comparison_config = compare.bitstream_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_activestorage.csv"
    dspace_input = "src/tests/assets/dspace_bitstream.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    print(f"{output_df.to_string()}")
    # First row
    assert output_df["name"][0] == "PASS"
    assert output_df["checksum"][0] == "PASS"
    assert output_df["sequence"][0] == "PASS"
    assert output_df["parent_item_id"][0] == "PASS"
    assert output_df["parent_item_name"][0] == "PASS"
    # Second row
    assert output_df["name"][1] == "PASS"
    assert output_df["checksum"][1] == "PASS"
    assert output_df["sequence"][1] == "PASS"
    assert output_df["parent_item_id"][1] == "PASS"
    assert output_df["parent_item_name"][1] == "PASS"


def test_input_process_item_valid(tmp_path):
    """
    Test process_input for a Item with valid data
    """
    comparison_config = compare.item_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_item.csv"
    dspace_input = "src/tests/assets/dspace_item.csv"
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
    assert output_df["collection_parent"][0] == "PASS"
    assert output_df["dc.title"][0] == "PASS"
    assert output_df["dc.contributor.author"][0] == "PASS"
    assert output_df["dc.contributor.other"][0] == "PASS"
    assert output_df["dc.language"][0] == "PASS"
    assert output_df["dc.subject"][0] == "PASS"
    assert output_df["dc.date.issued"][0] == "PASS"
    assert output_df["dc.rights"][0] == "PASS"
    assert output_df["dc.rights.license"][0] == "PASS"
    assert output_df["dc.type"][0] == "PASS"
    assert output_df["access_rights"][0] == "PASS"
