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
    return str1 == str2


# Scholaris removes trailing linebreaks
def string_compare_ignore_whitespace(str1, str2):
    """
    Compare two strings
    """
    # Remove all whitespace
    # Reconsider this approach?
    regex = re.compile(r"\s+")
    logging.debug("string_compare_ignore_whitespace: %s", regex.sub("", str(str1)))
    return (
        False
        if isinstance(str1, float) or isinstance(str2, float)
        else regex.sub("", str(str1)) == regex.sub("", str(str2))
    )


# Define the columns to compare and how to compare them
# "index_columns" is the key to use to align the two dataframes
# "comparison_types" is a dictionary of the columns to compare
# The key at the top level is the column name in the output file
# The columns key is a dictionary with the keys jupiter and dspace
# and value is the column name in the respective dataframes.
# The "comparison_function" is the function to use to compare the two columns
community_columns_to_compare = {
    "index_columns": {"jupiter": "title", "dspace": "name"},
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
# "comparison_types" is a dictionary of the columns to compare
# The key at the top level is the column name in the output file
# The columns key is a dictionary with the keys jupiter and dspace
# and value is the column name in the respective dataframes.
# The "comparison_function" is the function to use to compare the two columns
collection_columns_to_compare = {
    "index_columns": {"jupiter": "title", "dspace": "name"},
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

        if comparison_function(row[jupiter_column], row[dspace_column]):
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
    Process communities.
    """
    jupiter_df = pandas.read_csv(jupiter_input)
    dspace_df = pandas.read_csv(dspace_input)

    # Merge the two dataframes and align on the column values in the title/name
    # drop=False to keep the column in the dataframe
    jupiter_df.set_index(
        comparison_config["index_columns"]["jupiter"], inplace=True, drop=False
    )
    dspace_df.set_index(
        comparison_config["index_columns"]["dspace"], inplace=True, drop=False
    )

    # Outer join to keep all rows from both dataframesif missing from one or the other.
    # NAN if missing
    # If the dataframes have the same column names, the suffixes are added to the column names
    aligned_df = jupiter_df.join(
        dspace_df, how="outer", lsuffix="_jupiter", rsuffix="_dspace"
    )

    writer = csv.DictWriter(
        output_file,
        fieldnames=["index"] + list(comparison_config["comparison_types"].keys()),
    )
    writer.writeheader()

    # Iterate over the rows in the aligned dataframe and compare the columns
    for index, row in aligned_df.iterrows():
        comparison_output = {"index": index}
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
        # case "items":
        #    process_items(jupiter_input, dspace_input, output_file)
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
