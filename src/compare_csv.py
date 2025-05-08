# pylint: disable=too-many-lines
"""
Given two CSV files, compare the two files and return the differences between the two files.

venv/bin/python src/compare_csv.py \
    --input_jupiter ~/Downloads/era_export/jupiter_community_2025-03-06_12-05-19.csv \
    --input_dspace ~/Downloads/scholaris_communities.csv
    --output /tmp/z.csv
    --type communities

    Where
    * input_jupiter is the CSV file from the Jupiter export in the
        jupiter_output_scripts/juptiter_collection_metadata_to_CSV.rb
    * input_dspace is the CSV file from the dsapce_api_experiment.py
"""

import argparse
import base64
import csv
import logging
import os
import pathlib
import re
import sys

import pandas

from utils import utilities as utils


INVALID_CHARACTER_PATTERN = (
    r"["
    r"\u0000-\u0008"
    r"\u000B\u000C"
    r"\u000E-\u001F"
    r"\u007F-\u009F"
    r"\uFFFE\uFFFF"
    r"\U0001FFFE-\U0001FFFF"
    r"\U0010FFFE-\U0010FFFF"
    r"]"
)


def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        required=False,
        help="Object Type ['communities', 'collections', 'items'].",
        default="communities",
    )
    parser.add_argument(
        "--input_jupiter", required=True, help="CSV file from the Jupiter export."
    )
    parser.add_argument(
        "--input_dspace", required=True, help="CSV file from the Scholaris export."
    )
    parser.add_argument(
        "--output", required=True, help="Location to store output file."
    )
    parser.add_argument(
        "--logging_level", required=False, help="Logging level.", default="INFO"
    )

    return parser.parse_args()


#
def string_compare(str1, str2):
    """
    Compare two strings
    """
    logging.debug("|%s| ---- |%s|", str1, str2)
    return str1 == str2


def activestorage_to_dspace_checksum_compare(str1, str2):
    """
    Compare two checksums; Ruby ActiveStorage uses a base63 encoding plus md5
    """
    logging.debug("%s ---- %s", str1, str2)
    str1_md5_hex = base64.b64decode(str1).hex() if isinstance(str1, str) else ""

    logging.debug("%s ---- %s", str1_md5_hex, str2)
    return str1_md5_hex == str2


#
def access_rights_compare(str1, str2):
    """
    Compare access rights given the following mapping
    """
    access_rights = {
        "http://terms.library.ualberta.ca/public": "open.access",
        "http://terms.library.ualberta.ca/embargo": "embargo",
        "http://terms.library.ualberta.ca/authenticated": "restricted",
    }

    logging.debug("%s ---- %s", str1, str2)

    return (
        str2 == access_rights[str1]
        if isinstance(str1, str) and str1 in access_rights
        else False
    )


# Scholaris removes trailing linebreaks
def string_compare_ignore_whitespace(str1, str2):
    """
    Compare two strings
    """
    # Remove all whitespace
    # Reconsider this approach?
    regex = re.compile(r"\s+")
    ret = False
    if str(str1) == str(str2):
        ret = True
    else:
        ret = regex.sub("", str(str1)) == regex.sub("", str(str2))
    logging.debug(
        "|%s| ---- |%s| |%s|",
        str(str1),
        str(str2),
        str(ret),
    )
    return ret


def remove_xml_invalid_characters(str1):
    """
    Remove invalid characters:
    """
    return re.sub(INVALID_CHARACTER_PATTERN, "", str1)


def remove_carrage_return(str1):
    """
    Remove invalid characters:
    """
    return re.sub(r"\r", "", str1)


#
def abstract_compare(str1, list2):
    """
    Thesis abstract REST API result have <p></p> elements
    remove from comparison
    """
    logging.debug("%s ---- %s", str1, list2)
    if isinstance(str1, float):
        str1 = str(str1)
    else:
        str1 = remove_xml_invalid_characters(str1)
    list2 = "[]" if isinstance(list2, float) else list2
    list2 = list2.replace("<p>", "").replace("</p>", "")
    list2 = utils.convert_string_list_representation_to_list(list2)
    logging.debug("%s ---- %s", str1, list2)

    return True if not str1 and not list2 else str1 in list2


# Scholaris removes trailing linebreaks
def string_in_list_compare_ignore_whitespace(str1, list2):
    """
    Compare a string to a string representation of a list
    Item description is stored as an list of "things"
    """
    logging.debug("|%s| ---- %s", str1, list2)
    if isinstance(str1, float):
        str1 = str(str1)
    else:
        str1 = remove_xml_invalid_characters(str1)
        str1 = remove_carrage_return(str1)
    list2 = utils.convert_string_list_representation_to_list(list2)
    logging.debug("|%s| ---- %s", str1, list2)

    return True if not str1 and not list2 else str(str1).strip() in list2


#
def member_of_list_compare(list1, list2):
    """
    Compare two lists
    """
    logging.debug("%s ---- %s", list1, list2)
    return list1 == list2


#
def value_in_string_list_compare(str1, list2):
    """
    compare a simple string to the contents of a list represented as a string
    """
    logging.debug("%s ---- %s", str1, list2)
    list2 = utils.convert_string_list_representation_to_list(list2)
    logging.debug("%s ---- %s", str1, list2)

    return True if not str1 and not list2 else str(str1).strip() in list2


#
def string_lists_compare(list1, list2):
    """
    compare a the contents of two lists represented as a strings
    """
    logging.debug("%s ---- %s", list1, list2)
    list1 = utils.convert_string_list_representation_to_list(list1)
    list2 = utils.convert_string_list_representation_to_list(list2)
    logging.debug("%s ---- %s", list1, list2)
    return list1 == list2


#
def string_lists_compare_trim_whitespace(list1, list2):
    """
    compare a the contents of two lists represented as a strings
    Trim leading and trailing whitespace
    """
    logging.debug("%s ---- %s", list1, list2)
    tmp_list1 = utils.convert_string_list_representation_to_list(list1)
    tmp_list2 = utils.convert_string_list_representation_to_list(list2)
    tmp_list1 = [item.strip() for item in tmp_list2]
    logging.debug("%s ---- %s", tmp_list1, tmp_list2)
    return tmp_list1 == tmp_list2


#
def collection_parent_compare(list1, list2):
    """
    Compare two lists
    """
    logging.debug("%s ---- %s", list1, list2)

    # list 1 is nan if item not in Jupiter
    list1 = '[""]' if isinstance(list1, str) is False else list1

    logging.debug("%s ---- %s", list1, list2)

    list1_collection_ids = list(
        path.split("/")[1]
        for path in utils.convert_string_to_json(list1)
        if path and isinstance(list1, str)
    )

    if isinstance(list2, str) and list2.startswith("["):
        list2 = utils.convert_string_list_representation_to_list(list2)
    elif isinstance(list2, str):
        list2 = [list2]

    logging.debug("%s ---- %s", list1_collection_ids, list2)

    return list1_collection_ids == list2


#
def filename_with_uuid_compare(era_filename, scholaris_filename):
    """
    Compare filenames, allowing for Scholaris filenames to have a UUID appended.
    Example:
        ERA: a.pdf
        Scholaris: a_uuid.pdf
    """

    logging.debug("%s ---- %s", era_filename, scholaris_filename)
    print("%s ---- %s", era_filename, scholaris_filename)
    if not era_filename or not scholaris_filename:
        return False

    # Remove any whitespace and compare the base filename
    era_filename = era_filename.strip()
    scholaris_filename = scholaris_filename.strip()

    if scholaris_filename == era_filename:
        return True

    era_filename_without_type = era_filename.split(".")[0]
    # Check if the Scholaris filename starts with the ERA filename (before the UUID)
    if scholaris_filename.startswith(era_filename_without_type):
        # Ensure the Scholaris filename has a valid UUID appended after the base filename
        # Extract the suffix
        # slices with "black" styling in PEP 8 and
        # flake lint uses PEP 8 + PEP 257 thus tool flags spacing differently
        suffix = scholaris_filename[len(era_filename_without_type) :]  # noqa: E203
        if suffix.startswith("_") and len(suffix.split(".")[0]) > 1:
            return True

    return False


#
def special_language_compare(row, key, value):
    """
    Compare two lists of languages with a conversion step
    Adapted from https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac
    Jupiter Item: list value field "languages" (not the "s" in the name)
    Jupiter Thesis: single value field "language"
    """

    easy_language_mapping = {
        "http://id.loc.gov/vocabulary/iso639-2/eng": "en",
        "http://id.loc.gov/vocabulary/iso639-2/fre": "fr",
        "http://id.loc.gov/vocabulary/iso639-2/ger": "de",
        "http://id.loc.gov/vocabulary/iso639-2/ita": "it",
        "http://id.loc.gov/vocabulary/iso639-2/jpn": "ja",
        "http://id.loc.gov/vocabulary/iso639-2/spa": "es",
        "http://id.loc.gov/vocabulary/iso639-2/zho": "zh",
        "http://id.loc.gov/vocabulary/iso639-2/ukr": "uk",
        "http://id.loc.gov/vocabulary/iso639-2/rus": "ru",
        "http://id.loc.gov/vocabulary/iso639-2/zxx": "No linguistic content",
        "http://terms.library.ualberta.ca/other": "other",
    }
    logging.debug(": [%s] %s", key, value)

    jupiter_list_idx = value["columns"]["jupiter"][0]
    jupiter_str_idx = value["columns"]["jupiter"][1]
    dspace_idx = value["columns"]["dspace"]

    logging.debug(
        "|%s| |%s| --- |%s|",
        row[jupiter_list_idx],
        row[jupiter_str_idx],
        row[dspace_idx],
    )

    jupiter_list = []

    # test for nan (float "not-a-number")
    if not isinstance(row[jupiter_list_idx], float) and row[jupiter_list_idx] != "":
        jupiter_list = (
            utils.convert_string_list_representation_to_list(row[jupiter_list_idx])
            if row[jupiter_list_idx]
            else []
        )

    # test for nan (float "not-a-number")
    if not isinstance(row[jupiter_list_idx], float) and row[jupiter_str_idx] != "":
        jupiter_list.append(row[jupiter_str_idx])

    dspace_list = utils.convert_string_list_representation_to_list(row[dspace_idx])

    logging.debug("%s ---- %s", jupiter_list, dspace_list)
    conversion_result = list(
        easy_language_mapping[language] for language in jupiter_list if language
    )
    logging.debug("%s ---- %s", conversion_result, dspace_list)

    return "PASS" if conversion_result == dspace_list else "FAIL"


#
def item_or_thesis_jupiter_strings_to_single_dspace(row, key, value):
    """
    Special dc.issue_data comparison: jupiter item and thesis have different fields
    that migrated into a single dspace field
    """
    logging.debug(": [%s] %s", key, value)

    col_1 = row[value["columns"]["jupiter"][0]]
    col_2 = row[value["columns"]["jupiter"][1]]
    list_dspace = utils.convert_string_list_representation_to_list(
        row[value["columns"]["dspace"]]
    )
    list_dspace = [item.strip() for item in list_dspace]

    logging.debug(
        ": %s[%s] %s[%s] %s[%s]",
        value["columns"]["jupiter"][0],
        col_1,
        value["columns"]["jupiter"][1],
        col_2,
        value["columns"]["dspace"],
        list_dspace,
    )

    ret = "FAIL"
    if not col_1 and not col_2 and not list_dspace:
        ret = "PASS"
    elif col_1 in list_dspace or col_2 in list_dspace:
        ret = "PASS"
    return ret


#
def item_or_thesis_jupiter_list_and_string_to_single_dspace(row, key, value):
    """
    Special comparison: jupiter item and thesis have different fields, one list and one string
    that migrated into the Scholaris field
    """
    logging.debug(": [%s] %s", key, value)

    logging.debug(
        ": %s[%s] %s[%s] %s[%s]",
        value["columns"]["jupiter"][0],
        row[value["columns"]["jupiter"][0]],
        value["columns"]["jupiter"][1],
        row[value["columns"]["jupiter"][1]],
        value["columns"]["dspace"],
        row[value["columns"]["dspace"]],
    )

    list_1 = utils.convert_string_list_representation_to_list(
        row[value["columns"]["jupiter"][0]]
    )
    if isinstance(list_1, list):
        list_1 = [elem.strip() for elem in list_1]
    str_1 = row[value["columns"]["jupiter"][1]]
    str_1 = str_1.strip() if isinstance(str_1, str) else str_1
    list_dspace = utils.convert_string_list_representation_to_list(
        row[value["columns"]["dspace"]]
    )

    logging.debug(
        ": %s[%s] %s[%s] %s[%s]",
        value["columns"]["jupiter"][0],
        list_1,
        value["columns"]["jupiter"][1],
        str_1,
        value["columns"]["dspace"],
        list_dspace,
    )

    ret = "FAIL"
    if not list_1 and not str_1 and not list_dspace:
        ret = "PASS"
    elif list_1 == list_dspace or str_1 in list_dspace:
        ret = "PASS"
    return ret


#
def item_or_thesis_jupiter_lists_to_single_dspace(row, key, value):
    """
    Special comparison: jupiter item and thesis have different fields
    that migrated into the field
    """
    logging.debug(": [%s] %s", key, value)

    logging.debug(
        ": %s[%s] %s[%s] %s[%s]",
        value["columns"]["jupiter"][0],
        row[value["columns"]["jupiter"][0]],
        value["columns"]["jupiter"][1],
        row[value["columns"]["jupiter"][1]],
        value["columns"]["dspace"],
        row[value["columns"]["dspace"]],
    )

    list_1 = utils.convert_string_list_representation_to_list(
        row[value["columns"]["jupiter"][0]]
    )
    if isinstance(list_1, list):
        list_1 = [elem.strip() for elem in list_1]
    list_2 = utils.convert_string_list_representation_to_list(
        row[value["columns"]["jupiter"][1]]
    )
    if isinstance(list_2, list):
        list_2 = [elem.strip() for elem in list_2]
    list_dspace = utils.convert_string_list_representation_to_list(
        row[value["columns"]["dspace"]]
    )

    logging.debug(
        ": %s[%s] %s[%s] %s[%s]",
        value["columns"]["jupiter"][0],
        list_1,
        value["columns"]["jupiter"][1],
        list_2,
        value["columns"]["dspace"],
        list_dspace,
    )

    ret = "FAIL"
    if not list_1 and not list_2 and not list_dspace:
        ret = "PASS"
    elif list_dspace in (list_1, list_2):
        ret = "PASS"
    return ret


#
def special_type_compare(row, key, value):
    """
    Special type comparision
    """
    logging.debug("special_type_compare: [%s] %s", key, value)

    # Adapted from the original migration
    # https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac
    easy_item_type_mapping = {
        # Values to check when there are multiple entries
        "http://purl.org/ontology/bibo/Article": "http://purl.org/coar/resource_type/c_6501",
        "http://purl.org/ontology/bibo/status#draft": "http://purl.org/coar/version/c_b1a7d7d4d402bcce",
        "http://vivoweb.org/ontology/core#submitted": "http://purl.org/coar/version/c_71e4c1898caa6e32",
        # 'http://purl.org/ontology/bibo/Article': 'http://purl.org/coar/resource_type/c_6501',
        "http://purl.org/ontology/bibo/status#published": "http://purl.org/coar/version/c_970fb48d4fbd8a85",
        # Values mapped one to one
        "http://purl.org/ontology/bibo/Book": "http://purl.org/coar/resource_type/c_2f33",
        "http://purl.org/ontology/bibo/Chapter": "http://purl.org/coar/resource_type/c_3248",
        "http://purl.org/ontology/bibo/Image": "http://purl.org/coar/resource_type/c_c513",
        "http://purl.org/ontology/bibo/Report": "http://purl.org/coar/resource_type/c_93fc",
        "http://terms.library.ualberta.ca/researchMaterial": "http://purl.org/coar/resource_type/c_1843",
        "http://vivoweb.org/ontology/core#Presentation": "http://purl.org/coar/resource_type/R60J-J5BD",
        "http://vivoweb.org/ontology/core#ConferencePoster": "http://purl.org/coar/resource_type/c_6670",
        "http://vivoweb.org/ontology/core#Dataset": "http://purl.org/coar/resource_type/c_ddb1",
        "http://vivoweb.org/ontology/core#Review": "http://purl.org/coar/resource_type/c_efa0",
        "http://terms.library.ualberta.ca/learningObject": "http://purl.org/coar/resource_type/c_e059",
    }

    # nan float if jupiter item not found
    list1 = (
        [row[value["columns"]["jupiter"][0]]]
        if isinstance(row[value["columns"]["jupiter"][0]], str)
        else []
    )
    if (
        isinstance(row[value["columns"]["jupiter"][1]], str)
        and row[value["columns"]["jupiter"][1]]
    ):
        list1 = list1 + utils.convert_string_list_representation_to_list(
            row[value["columns"]["jupiter"][1]]
        )

    logging.debug("special_type_compare: %s", list1)

    list1 = list(easy_item_type_mapping[type] for type in list1 if type)
    list2 = utils.convert_string_list_representation_to_list(
        row[value["columns"]["dspace"]]
    )
    # list2: if multiple values, they are separated with a space character
    list2 = [item for sublist in list2 for item in sublist.split(" ")]

    logging.debug("special_type_compare: %s ---- %s", list1, list2)

    ret = "FAIL"
    if list1 == list2:
        ret = "PASS"
    elif not list1 and list2 == ["http://purl.org/coar/resource_type/c_46ec"]:
        ret = "STATIC VALUE ADDED (thesis?)"
    return ret


# Define the columns to compare and how to compare them
# "index_columns" is the key to use to align the two dataframes
# "comparison_types" is a dictionary of the columns to compare
# The key at the top level is the column name in the output file
# The columns key is a dictionary with the keys jupiter and dspace
# and value is the column name in the respective dataframes.
# The "comparison_function" is the function to use to compare the two columns
community_columns_to_compare = {
    "index_columns": {"jupiter": "title", "dspace": "name"},
    "label_column": "name",
    "identifier": {"jupiter": "id", "dspace": "uuid"},
    "last_modified": {"jupiter": "updated_at", "dspace": "lastModified"},
    "comparison_types": {
        "name": {
            "columns": {"jupiter": "title", "dspace": "name"},
            "comparison_function": string_compare,
        },
        "description": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description",
            },
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "abstract": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description.abstract",
            },
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "dc.title": {
            "columns": {"jupiter": "title", "dspace": "metadata.dc.title"},
            "comparison_function": value_in_string_list_compare,
        },
    },
}

# Define the columns to compare and how to compare them
# "index_columns" is the key to use to align the two dataframes
#    Examples:
#    "index_columns": {"jupiter": "title", "dspace": "name"},
#    "index_columns": {"jupiter": "id", "dspace": "provenance.ual.jupiterId.collection"},
# "comparison_types" is a dictionary of the columns to compare
# The key at the top level is the column name in the output file
# The columns key is a dictionary with the keys jupiter and dspace
# and value is the column name in the respective dataframes.
# The "comparison_function" is the function to use to compare the two columns
collection_columns_to_compare = {
    "index_columns": {"jupiter": "id", "dspace": "provenance.ual.jupiterId.collection"},
    "label_column": "name",
    "identifier": {"jupiter": "id", "dspace": "uuid"},
    "last_modified": {"jupiter": "updated_at", "dspace": "lastModified"},
    "comparison_types": {
        "name": {
            "columns": {"jupiter": "title", "dspace": "name"},
            "comparison_function": string_compare_ignore_whitespace,
        },
        "description": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description",
            },
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "abstract": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description.abstract",
            },
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "dc.title": {
            "columns": {"jupiter": "title", "dspace": "metadata.dc.title"},
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "collection_parent_expect_to_fail_due_to_lack_of_community_provenance": {
            "columns": {
                "jupiter": "community.title",
                "dspace": "provenance.ual.jupiterId.community",
            },
            "comparison_function": string_compare,
        },
    },
}

# Define the columns to compare and how to compare them
# "index_columns" is the key to use to align the two dataframes
#    Examples:
#    "index_columns": {"jupiter": "title", "dspace": "name"},
#    "index_columns": {"jupiter": "id", "dspace": "provenance.ual.jupiterId.collection"},
# "comparison_types" is a dictionary of the columns to compare
#   The key at the top level is the column name in the output file
#   The columns key is a dictionary with the keys jupiter and dspace
#   and value is the column name in the respective dataframes.
#   The "comparison_function" is the function to use to compare the two columns
#   "_jupiter"/"_dspace" suffixes are added to the column names if the dataframes
#       have the same column names, required for multi-index dataframe joins
bitstream_columns_to_compare = {
    "index_columns": {
        "jupiter": ["provenance.ual.jupiterId.item", "bitstream.sequenceId"],
        "dspace": ["provenance.ual.jupiterId.item", "bitstream.sequenceId"],
    },
    "label_column": "item.name",
    "identifier": {"jupiter": "item.id", "dspace": "item.uuid"},
    "last_modified": {"jupiter": "created_at", "dspace": None},
    "comparison_types": {
        "name": {
            "columns": {"jupiter": "filename", "dspace": "bitstream.name"},
            "comparison_function": filename_with_uuid_compare,
        },
        "checksum": {
            "columns": {
                "jupiter": "checksum",
                "dspace": "bitstream.checksum.value",
            },
            "comparison_function": activestorage_to_dspace_checksum_compare,
        },
        "sequence": {
            "columns": {
                "jupiter": "bitstream.sequenceId_jupiter",
                "dspace": "bitstream.sequenceId_dspace",
            },
            "comparison_function": string_compare,
        },
        "parent_item_id": {
            "columns": {
                "jupiter": "provenance.ual.jupiterId.item_jupiter",
                "dspace": "provenance.ual.jupiterId.item_dspace",
            },
            "comparison_function": string_compare,
        },
        "parent_item_name": {
            "columns": {"jupiter": "item.title", "dspace": "item.name"},
            "comparison_function": string_compare_ignore_whitespace,
        },
    },
}

# Define the columns to compare and how to compare them
# "index_columns" is the key to use to align the two dataframes
#    Examples:
#    "index_columns": {"jupiter": "title", "dspace": "name"},
#    "index_columns": {"jupiter": "id", "dspace": "provenance.ual.jupiterId.collection"},
# "comparison_types" is a dictionary of the columns to compare
# The key at the top level is the column name in the output file
# The columns key is a dictionary with the keys jupiter and dspace
# and value is the column name in the respective dataframes.
# The "comparison_function" is the function to use to compare the two columns
#
# Item: title, type, languages, author/creator, subjects, created/issued date, license/rights
# Thesis: title, dissertant, abstract, graduation date, subjects, rights
# Permissions attached to a bitstream bundle (HAL accessStatus)

item_columns_to_compare = {
    "index_columns": {"jupiter": "id", "dspace": "metadata.ual.jupiterId"},
    "label_column": "name",
    "identifier": {"jupiter": "id", "dspace": "uuid"},
    "last_modified": {"jupiter": "updated_at", "dspace": "lastModified"},
    "comparison_types": {
        "name": {
            "columns": {"jupiter": "title", "dspace": "name"},
            "comparison_function": string_compare_ignore_whitespace,
        },
        "description": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description",
            },
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "collection_parent": {
            "columns": {
                "jupiter": "member_of_paths",
                "dspace": "provenance.ual.jupiterId.collection",
            },
            "comparison_function": collection_parent_compare,
        },
        "dc.title": {
            "columns": {"jupiter": "title", "dspace": "metadata.dc.title"},
            "comparison_function": value_in_string_list_compare,
        },
        "dc.contributor.other": {
            "columns": {
                "jupiter": ["contributors", "committee_members"],
                "dspace": "metadata.dc.contributor.other",
            },
            "comparison_function": item_or_thesis_jupiter_lists_to_single_dspace,
        },
        "dc.contributor.author": {
            "columns": {
                "jupiter": ["creators", "dissertant"],
                "dspace": "metadata.dc.contributor.author",
            },
            "comparison_function": item_or_thesis_jupiter_list_and_string_to_single_dspace,
        },
        "dc.type": {
            "columns": {
                "jupiter": ["item_type", "publication_status"],
                "dspace": "metadata.dc.type",
            },
            "comparison_function": special_type_compare,
        },
        "dc.language": {
            "columns": {
                "jupiter": ["languages", "language"],
                "dspace": "metadata.dc.language.iso",
            },
            "comparison_function": special_language_compare,
        },
        "dc.subject": {
            "columns": {"jupiter": "subject", "dspace": "metadata.dc.subject"},
            "comparison_function": string_lists_compare_trim_whitespace,
        },
        "dc.date.issued": {
            "columns": {
                "jupiter": ["created", "graduation_date"],
                "dspace": "metadata.dc.date.issued",
            },
            "comparison_function": item_or_thesis_jupiter_strings_to_single_dspace,
        },
        "dc.rights": {
            "columns": {"jupiter": "rights", "dspace": "metadata.dc.rights"},
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "dc.rights.uri": {
            "columns": {"jupiter": "license", "dspace": "metadata.dc.rights.uri"},
            "comparison_function": string_in_list_compare_ignore_whitespace,
        },
        "abstract": {
            "columns": {
                "jupiter": "abstract",
                "dspace": "metadata.dc.description.abstract",
            },
            "comparison_function": abstract_compare,
        },
        "access_rights": {
            "columns": {"jupiter": "visibility", "dspace": "access_rights"},
            "comparison_function": access_rights_compare,
        },
        # "if_thesis_degree.discipline": {
        #     "columns": {"jupiter": "", "dspace": "metadata.thesis.degree.discipline"},
        #     "comparison_function": value_in_string_list_compare,
        # },
        # "if_thesis_dissertant": {
        #    "columns": {
        #        "jupiter": "dissertant",
        #        "dspace": "metadata.dc.contributor.author",
        #    },
        #    "comparison_function": value_in_string_list_compare,
        # },
        "if_thesis_supervisor": {
            "columns": {
                "jupiter": "supervisors",
                "dspace": "metadata.dc.contributor.advisor",
            },
            "comparison_function": string_lists_compare,
        },
        # "if_thesis_committee_members": {
        #    "columns": {
        #        "jupiter": "committee_members",
        #        "dspace": "metadata.dc.contributor.other",
        #    },
        #    "comparison_function": string_lists_compare,
        # },
        "if_thesis_degree.grantor": {
            "columns": {
                "jupiter": "institution",
                "dspace": "metadata.thesis.degree.grantor",
            },
            "comparison_function": value_in_string_list_compare,
        },
        "if_thesis_degree.level": {
            "columns": {
                "jupiter": "thesis_level",
                "dspace": "metadata.thesis.degree.level",
            },
            "comparison_function": value_in_string_list_compare,
        },
        "if_thesis_degree.name": {
            "columns": {"jupiter": "degree", "dspace": "metadata.thesis.degree.name"},
            "comparison_function": value_in_string_list_compare,
        },
        # "if_thesis_data.graduation": {
        #    "columns": {
        #        "jupiter": "graduation_date",
        #        "dspace": "metadata.ual.date.graduation",
        #    },
        #    "comparison_function": value_in_string_list_compare,
        # },
        "if_thesis_ual.department": {
            "columns": {"jupiter": "departments", "dspace": "metadata.ual.department"},
            "comparison_function": string_lists_compare,
        },
    },
}


#
def process_row(row, columns_to_compare):
    """
    Process a row based on the configuration in columns_to_compare
    """
    comparison_output = {}
    for key, value in columns_to_compare.items():
        jupiter_column = f"{value['columns']['jupiter']}"
        dspace_column = f"{value['columns']['dspace']}"
        comparison_function = value["comparison_function"]

        logging.debug(
            "comparison [%s]: jupiter_column [%s] --- dspace_column [%s]",
            comparison_function.__name__,
            jupiter_column,
            dspace_column,
        )

        if comparison_function.__name__ in [
            "special_type_compare",
            "special_language_compare",
            "item_or_thesis_jupiter_strings_to_single_dspace",
            "item_or_thesis_jupiter_list_and_string_to_single_dspace",
            "item_or_thesis_jupiter_lists_to_single_dspace",
        ]:
            # special comparison function
            comparison_output[key] = comparison_function(row, key, value)
        elif comparison_function(row[jupiter_column], row[dspace_column]):
            comparison_output[key] = "PASS"
        else:
            comparison_output[key] = "FAIL"

        logging.debug("key: [%s] status:[%s]", key, comparison_output[key])

    return comparison_output


#
def process_input(
    jupiter_input,
    dspace_input,
    output_file,
    comparison_config,
):
    """
    Process input from Jupiter and DSpace.
    """
    # dtype=str for all to avoid mixed type errors
    #   DtypeWarning: Columns (35) have mixed types. Specify dtype option on import or set low_memory=False.
    jupiter_df = pandas.read_csv(jupiter_input, keep_default_na=False, dtype=str)
    dspace_df = pandas.read_csv(dspace_input, keep_default_na=False, dtype=str)

    # Merge the two dataframes and align on the column values in the title/name
    # drop=False to keep the column in the dataframe
    jupiter_df.set_index(
        comparison_config["index_columns"]["jupiter"], inplace=True, drop=False
    )
    dspace_df.set_index(
        comparison_config["index_columns"]["dspace"], inplace=True, drop=False
    )

    # Outer join to keep all rows from both dataframes if missing from one or the other.
    # NAN if missing
    # If the dataframes have the same column names, the suffixes are added to the column names
    aligned_df = jupiter_df.join(
        dspace_df, how="outer", lsuffix="_jupiter", rsuffix="_dspace"
    )

    writer = csv.DictWriter(
        output_file,
        fieldnames=[
            "index (empty if no ERA obj)",
            "label",
            "jupiter_updated_at",
            "dspace_lastModified",
            "jupiter_id",
            "dspace_id",
        ]
        + list(comparison_config["comparison_types"].keys()),
    )
    writer.writeheader()

    # Iterate over the rows in the aligned dataframe and compare the columns
    for index, row in aligned_df.iterrows():

        logging.debug("ID [%s]", index)

        comparison_output = {
            "index (empty if no ERA obj)": index,
            "label": row[comparison_config["label_column"]],
        }
        if comparison_config["last_modified"]["jupiter"] is not None:
            comparison_output.update(
                {
                    "jupiter_updated_at": row[
                        comparison_config["last_modified"]["jupiter"]
                    ]
                }
            )
        if comparison_config["last_modified"]["dspace"] is not None:
            comparison_output.update(
                {
                    "dspace_lastModified": row[
                        comparison_config["last_modified"]["dspace"]
                    ]
                }
            )
        if comparison_config["identifier"]["jupiter"] is not None:
            comparison_output.update(
                {"jupiter_id": row[comparison_config["identifier"]["jupiter"]]}
            )
        if comparison_config["identifier"]["dspace"] is not None:
            comparison_output.update(
                {"dspace_id": row[comparison_config["identifier"]["dspace"]]}
            )
        comparison_output.update(
            process_row(row, comparison_config["comparison_types"])
        )
        logging.debug("output: [%s]", comparison_output)
        writer.writerow(comparison_output)


#
def process(jupiter_input, dspace_input, output_file, data_type):
    """
    Main processing function
    """

    match data_type:
        case "communities":
            process_input(
                jupiter_input,
                dspace_input,
                output_file,
                community_columns_to_compare,
            )
        case "collections":
            process_input(
                jupiter_input,
                dspace_input,
                output_file,
                collection_columns_to_compare,
            )
        case "bitstreams":
            process_input(
                jupiter_input,
                dspace_input,
                output_file,
                bitstream_columns_to_compare,
            )
        case "items":
            process_input(
                jupiter_input,
                dspace_input,
                output_file,
                item_columns_to_compare,
            )
        case _:
            logging.error("Unsupported DSO Type: %s", type)
            sys.exit()


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    # Configure logging
    log_level = getattr(logging, args.logging_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.log}")
    # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    logging.getLogger().setLevel(log_level)

    pathlib.Path(os.path.dirname(args.output)).mkdir(parents=True, exist_ok=True)
    with open(args.output, "wt", encoding="utf-8", newline="") as output_file:
        process(args.input_jupiter, args.input_dspace, output_file, args.type)


#
if __name__ == "__main__":
    main()
