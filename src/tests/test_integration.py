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


def test_activestorage_to_dspace_checksum_compare():
    """
    Test checksum comparisons
    """
    assert (
        compare.activestorage_to_dspace_checksum_compare(
            "joLf+gnmKnDv4/ZSUQjD9g==", "8e82dffa09e62a70efe3f6525108c3f6"
        )
        is True
    )
    assert compare.activestorage_to_dspace_checksum_compare(float("NaN"), "") is True
    assert (
        compare.activestorage_to_dspace_checksum_compare(
            float("NaN"), "8e82dffa09e62a70efe3f6525108c3f6"
        )
        is False
    )


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


def test_abstract_compare():
    """
    Test abstract
    """
    assert compare.abstract_compare("a", "['a']") is True
    assert compare.abstract_compare("a", "['<p>a</p>']") is True
    assert compare.abstract_compare("a. ", "['<p>a. </p>']") is True
    assert compare.abstract_compare(float("NaN"), "['']") is False
    assert (
        compare.abstract_compare(
            "\u0000\u0008\u000b\u000c\u000e\u001f\u007f\u009f", "['']"
        )
        is True
    )


def test_string_in_list_compare_ignore_whitespace():
    """
    Strip trailing and leading whitespace (e.g., description in Jupiter)
    """
    assert compare.string_in_list_compare_ignore_whitespace("asdf", "['asdf']") is True
    assert compare.string_in_list_compare_ignore_whitespace("f ", "['f']") is True
    # Missing "Nan" in DataFrame, we don't want it to match empty
    assert (
        compare.string_in_list_compare_ignore_whitespace(float("NaN"), "['']") is False
    )
    assert (
        compare.string_in_list_compare_ignore_whitespace(
            "\u0000\u0008\u000b\u000c\u000e\u001f\u007f\u009f", "['']"
        )
        is True
    )


def test_member_of_list_compare():
    """
    Test member_of_list_compare
    """
    assert compare.member_of_list_compare(["a", "b", "c"], ["a", "b", "c"]) is True
    assert compare.member_of_list_compare([], []) is True
    assert compare.member_of_list_compare(["a", "b", "c"], ["c", "b", "a"]) is False
    assert compare.member_of_list_compare(["a", "b", "c"], ["a"]) is False
    assert compare.member_of_list_compare(["a", "b", "c"], ["1"]) is False


def test_value_in_string_list_compare():
    """
    Given a single value string compare to string representation of a list
    """
    assert compare.value_in_string_list_compare("a", "['a']") is True
    assert compare.value_in_string_list_compare("a ", "['a']") is True
    assert compare.value_in_string_list_compare("", float("NaN")) is True
    assert compare.value_in_string_list_compare("", "[]") is True


def test_string_lists_compare():
    """
    compare to string representations of lists
    """
    assert compare.string_lists_compare("['a','b']", "['a','b']") is True
    assert compare.string_lists_compare("['a','b']", "['b','a']") is False
    assert compare.string_lists_compare("", "[]") is True


def test_string_lists_compare_trim_whitespace():
    """
    compare to string representations of lists; ignore leading and trailing whitespace
    """
    assert (
        compare.string_lists_compare_trim_whitespace("['a','b']", "['a','b']") is True
    )
    assert (
        compare.string_lists_compare_trim_whitespace("['a','b']", "['b','a']") is True
    )
    assert (
        compare.string_lists_compare_trim_whitespace("[' c','d ']", "['c','d']") is True
    )
    assert compare.string_lists_compare_trim_whitespace("", "[]") is True


def test_collection_parent_compare():
    """
    Test the Jupiter member_of_path compared to the Scholaris collection id
    """
    assert compare.collection_parent_compare('["a/b"]', "['b']") is True
    assert compare.collection_parent_compare('["a/bbb"]', "bbb") is True
    assert compare.collection_parent_compare('["a/b"]', "['c']") is False
    assert compare.collection_parent_compare("[]", float("NaN")) is False

def test_filename_with_uuid_compare():
    """
    Test the filename with uuid
    """
    assert compare.filename_with_uuid_compare("a.pdf", "a.pdf") == True
    assert compare.filename_with_uuid_compare("a.pdf", "b.pdf") == False
    assert compare.filename_with_uuid_compare("a.pdf", "a_12345.pdf") == True
    assert compare.filename_with_uuid_compare("a.pdf", "a.pdf_extra") == False
    assert compare.filename_with_uuid_compare("a.pdf", None) == False
    assert compare.filename_with_uuid_compare(None, "a_uuid.pdf") == False

def test_language_compare():
    """
    Language tests
    """
    item_column_key = "languages"
    thesis_column_key = "language"
    dspace_column_key = "metadata.dc.language.iso"
    key = "dc.language"
    value = {
        "columns": {
            "jupiter": [item_column_key, thesis_column_key],
            "dspace": dspace_column_key,
        }
    }

    # Test item where only "languages" is set
    item_column_value = "['http://id.loc.gov/vocabulary/iso639-2/jpn', 'http://id.loc.gov/vocabulary/iso639-2/fre']"
    thesis_column_value = ""
    dspace_column_value = "['ja', 'fr']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert compare.special_language_compare(row, key, value) == "PASS"

    # Test thesis where only "language" is set
    item_column_value = ""
    thesis_column_value = "http://id.loc.gov/vocabulary/iso639-2/eng"
    dspace_column_value = "['en']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }
    assert compare.special_language_compare(row, key, value) == "PASS"

    item_column_value = float("NaN")
    thesis_column_value = float("NaN")
    dspace_column_value = "[]"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }
    assert compare.special_language_compare(row, key, value) == "PASS"


def test_special_type_compare():
    """
    Test an item field or thesis field if different names againsta a single dspace field
    """
    item_column_key = "item_type"
    thesis_column_key = "publication_status"
    dspace_column_key = "metadata.dc.type"
    key = "dc.type"
    value = {
        "columns": {
            "jupiter": [item_column_key, thesis_column_key],
            "dspace": dspace_column_key,
        }
    }

    item_column_value = "http://purl.org/ontology/bibo/Book"
    thesis_column_value = ""
    dspace_column_value = "['http://purl.org/coar/resource_type/c_2f33']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert compare.special_type_compare(row, key, value) == "PASS"

    item_column_value = "http://purl.org/ontology/bibo/Article"
    thesis_column_value = """[
        'http://vivoweb.org/ontology/core#submitted',
        'http://purl.org/ontology/bibo/status#draft'
        ]"""
    dspace_column_value = """[
        'http://purl.org/coar/resource_type/c_6501',
        'http://purl.org/coar/version/c_71e4c1898caa6e32',
        'http://purl.org/coar/version/c_b1a7d7d4d402bcce'
        ]"""
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert compare.special_type_compare(row, key, value) == "PASS"

    item_column_value = ""
    thesis_column_value = ""
    dspace_column_value = "['http://purl.org/coar/resource_type/c_46ec']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.special_type_compare(row, key, value) == "STATIC VALUE ADDED (thesis?)"
    )


def test_item_or_thesis_jupiter_strings_to_single_dspace():
    """
    Test an item field or thesis field if different names againsta a single dspace field
    """
    item_column_key = "created"
    thesis_column_key = "graduation_date"
    dspace_column_key = "metadata.dc.date.issued"
    key = "dc.date_issued"
    value = {
        "columns": {
            "jupiter": [item_column_key, thesis_column_key],
            "dspace": dspace_column_key,
        }
    }

    item_column_value = "2999"
    thesis_column_value = ""
    dspace_column_value = "['2999']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.item_or_thesis_jupiter_strings_to_single_dspace(row, key, value)
        == "PASS"
    )

    item_column_value = ""
    thesis_column_value = "3000"
    dspace_column_value = "['3000']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.item_or_thesis_jupiter_strings_to_single_dspace(row, key, value)
        == "PASS"
    )


def test_item_or_thesis_jupiter_lists_to_single_dspace():
    """
    Test an item field or thesis field if different names againsta a single dspace field
    """
    item_column_key = "contributors"
    thesis_column_key = "committee_members"
    dspace_column_key = "metadata.dc.contributor.other"
    key = "dc.contributor.other"
    value = {
        "columns": {
            "jupiter": [item_column_key, thesis_column_key],
            "dspace": dspace_column_key,
        }
    }

    item_column_value = "['A ']"
    thesis_column_value = ""
    dspace_column_value = "['A']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.item_or_thesis_jupiter_lists_to_single_dspace(row, key, value) == "PASS"
    )

    item_column_value = ""
    thesis_column_value = "['B']"
    dspace_column_value = "['B']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.item_or_thesis_jupiter_lists_to_single_dspace(row, key, value) == "PASS"
    )


def test_item_or_thesis_jupiter_list_and_string_to_single_dspace():
    """
    Test an item field or thesis field if different names againsta a single dspace field
    """
    item_column_key = "creators"
    thesis_column_key = "dissertant"
    dspace_column_key = "metadata.dc.contributor.author"
    key = "dc.contributor.author"
    value = {
        "columns": {
            "jupiter": [item_column_key, thesis_column_key],
            "dspace": dspace_column_key,
        }
    }

    item_column_value = "['A ']"
    thesis_column_value = ""
    dspace_column_value = "['A']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.item_or_thesis_jupiter_list_and_string_to_single_dspace(row, key, value)
        == "PASS"
    )

    item_column_value = ""
    thesis_column_value = "B"
    dspace_column_value = "['B']"
    row = {
        item_column_key: item_column_value,
        thesis_column_key: thesis_column_value,
        dspace_column_key: dspace_column_value,
    }

    assert (
        compare.item_or_thesis_jupiter_list_and_string_to_single_dspace(row, key, value)
        == "PASS"
    )


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
    jupiter_input = "src/tests/assets/jupiter_combined_item.csv"
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
    assert output_df["dc.language"][0] == "PASS"
    assert output_df["dc.subject"][0] == "PASS"
    assert output_df["dc.date.issued"][0] == "PASS"
    assert output_df["dc.rights"][0] == "PASS"
    assert output_df["dc.rights.uri"][0] == "PASS"
    assert output_df["dc.type"][0] == "PASS"
    assert output_df["access_rights"][0] == "PASS"


def test_input_process_thesis_valid(tmp_path):
    """
    Test process_input for a Thesis with valid data
    """
    comparison_config = compare.item_columns_to_compare
    jupiter_input = "src/tests/assets/jupiter_combined_thesis.csv"
    dspace_input = "src/tests/assets/dspace_thesis.csv"
    tmp_file = tmp_path / "output.csv"

    with open(tmp_file, "wt", encoding="utf-8", newline="") as output_file:
        compare.process_input(
            jupiter_input,
            dspace_input,
            output_file,
            comparison_config,
        )

    output_df = pandas.read_csv(tmp_file)
    print(output_df.to_string())
    assert output_df["name"][0] == "PASS"
    assert output_df["abstract"][0] == "PASS"
    assert output_df["collection_parent"][0] == "PASS"
    assert output_df["dc.title"][0] == "PASS"
    assert output_df["dc.contributor.author"][0] == "PASS"
    assert output_df["dc.language"][0] == "PASS"
    assert output_df["dc.subject"][0] == "PASS"
    assert output_df["dc.date.issued"][0] == "PASS"
    assert output_df["dc.rights"][0] == "PASS"
    assert output_df["dc.rights.uri"][0] == "PASS"
    assert output_df["dc.type"][0] == "STATIC VALUE ADDED (thesis?)"
    assert output_df["access_rights"][0] == "PASS"
