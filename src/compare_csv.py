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
import csv
import logging
import json
import os
import pathlib
import re
import sys

import pandas


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
    logging.debug("string_compare: %s ---- %s", str1, str2)
    return str1 == str2


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
        "string_compare_ignore_whitespace: %s ---- %s %s",
        str(str1),
        str(str2),
        str(ret),
    )
    return ret


#
def member_of_list_compare(list1, list2):
    """
    Compare two lists
    """
    logging.debug("member_of_list_compare: %s ---- %s", list1, list2)
    return list1 == list2


#
def collection_parent_compare(list1, list2):
    """
    Compare two lists
    """
    logging.debug("member_of_list_compare: %s ---- %s", list1, list2)
    list1_collection_ids = list(
        path.split("/")[1] for path in json.loads(list1) if path
    )
    return list1_collection_ids == json.loads(list2)


#
def language_compare(list1, list2):
    """
    Compare two lists of languages with a conversion step
    Adapted from https://gist.github.com/lagoan/839cf8ce997fa17b529d84776b91cdac
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
    logging.debug("member_of_list_compare: %s ---- %s", list1, list2)
    conversion_result = list(
        easy_language_mapping[language] for language in json.loads(list1) if language
    )
    return conversion_result == json.loads(list2)


#
def special_type_compare(row, key, value):
    """
    Special type comparision
    """
    logging.debug("special_type_compare: [%s] %s ---- %s", key, value, row)

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

    list1 = [row[value["columns"]["jupiter"][0]]] + json.loads(
        row[value["columns"]["jupiter"][1]]
    )
    # str1 = " ".join(easy_item_type_mapping[type] for type in list1 if type)
    list1 = list(easy_item_type_mapping[type] for type in list1 if type)
    list2 = json.loads(row[value["columns"]["dspace"]])

    logging.debug("special_type_compare: %s ---- %s", list1, list2)

    return "PASS" if list1 == list2 else "FAIL"


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
                "dspace": "metadata.dc.description.0.value",
            },
            "comparison_function": string_compare_ignore_whitespace,
        },
        "abstract": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description.abstract.0.value",
            },
            "comparison_function": string_compare_ignore_whitespace,
        },
        "dc.title": {
            "columns": {"jupiter": "title", "dspace": "metadata.dc.title.0.value"},
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
            "comparison_function": string_compare,
        },
        "description": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description.0.value",
            },
            "comparison_function": string_compare_ignore_whitespace,
        },
        "abstract": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description.abstract.0.value",
            },
            "comparison_function": string_compare_ignore_whitespace,
        },
        "dc.title": {
            "columns": {"jupiter": "title", "dspace": "metadata.dc.title.0.value"},
            "comparison_function": string_compare,
        },
        "collection_parent_expect_to_fail_due_to_lack_of_community_provenance": {
            "columns": {
                "jupiter": "community.label",
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
    "identifier": {"jupiter": "provenance.ual.jupiterId.item", "dspace": "item.id"},
    "last_modified": {"jupiter": "created_at", "dspace": None},
    "comparison_types": {
        "name": {
            "columns": {"jupiter": "filename", "dspace": "bitstream.name"},
            "comparison_function": string_compare,
        },
        "checksum": {
            "columns": {
                "jupiter": "checksum",
                "dspace": "bitstream.checksum.value",
            },
            "comparison_function": string_compare,
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
                "dspace": "provenance.ual.jupiterId.item_jupiter",
            },
            "comparison_function": string_compare,
        },
        "parent_item_name": {
            "columns": {"jupiter": "item.title", "dspace": "item.name"},
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
            "comparison_function": string_compare,
        },
        "description": {
            "columns": {
                "jupiter": "description",
                "dspace": "metadata.dc.description.0.value",
            },
            "comparison_function": string_compare_ignore_whitespace,
        },
        "collection_parent": {
            "columns": {
                "jupiter": "member_of_paths",
                "dspace": "metadata.ual.jupiterCollection",
            },
            "comparison_function": collection_parent_compare,
        },
        "dc.title": {
            "columns": {"jupiter": "title", "dspace": "metadata.dc.title.0.value"},
            "comparison_function": string_compare,
        },
        "dc.contributor.author": {
            "columns": {
                "jupiter": "creators" "",
                "dspace": "metadata.dc.contributor.author",
            },
            "comparison_function": member_of_list_compare,
        },
        "dc.contributor.other": {
            "columns": {
                "jupiter": "contributors" "",
                "dspace": "metadata.dc.contributor.other",
            },
            "comparison_function": member_of_list_compare,
        },
        "dc.type": {
            "columns": {
                "jupiter": ["item_type", "publication_status"],
                "dspace": "metadata.dc.type",
            },
            "comparison_function": special_type_compare,
        },
        "dc.language": {
            "columns": {"jupiter": "languages", "dspace": "metadata.dc.language.iso"},
            "comparison_function": language_compare,
        },
        "dc.subject": {
            "columns": {"jupiter": "subject", "dspace": "metadata.dc.subject"},
            "comparison_function": member_of_list_compare,
        },
        "dc.date.issued": {
            "columns": {"jupiter": "created", "dspace": "metadata.dc.date.issued"},
            "comparison_function": string_compare,
        },
        "dc.rights": {
            "columns": {"jupiter": "rights", "dspace": "metadata.dc.rights"},
            "comparison_function": member_of_list_compare,
        },
        "dc.rights.license": {
            "columns": {"jupiter": "license", "dspace": "metadata.dc.rights.license"},
            "comparison_function": member_of_list_compare,
        },
        # "dissertant": {
        #    "columns": {"jupiter": "", "dspace": "metadata.dissertant"},
        #    "comparison_function": string_compare,
        # },
        # "abstract": {
        #     "columns": {"jupiter": "", "dspace": "metadata.dc.abstract"},
        #     "comparison_function": string_compare,
        # },
        # "graduation_date": {
        #     "columns": {"jupiter": "", "dspace": "metadata.graduation_date"},
        #     "comparison_function": string_compare,
        # },
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

        if key == "dc.type":
            comparison_output[key] = comparison_function(row, key, value)
        elif comparison_function(row[jupiter_column], row[dspace_column]):
            comparison_output[key] = "PASS"
        else:
            comparison_output[key] = "FAIL"
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
    jupiter_df = pandas.read_csv(jupiter_input, keep_default_na=False)
    dspace_df = pandas.read_csv(dspace_input, keep_default_na=False)

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
        if comparison_config["identifier"]["dspace"] is not None:
            comparison_output.update(
                {"dspace_id": row[comparison_config["identifier"]["dspace"]]}
            )
        if comparison_config["identifier"]["jupiter"] is not None:
            comparison_output.update(
                {"jupiter_id": row[comparison_config["identifier"]["dspace"]]}
            )
        comparison_output.update(
            process_row(row, comparison_config["comparison_types"])
        )
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
