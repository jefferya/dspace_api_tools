"""
Jupiter has separate models for Item and Thesis types while DSapce has a single model
with different optional fields. this script takes the two separate CSV from Jupiter
and combines into one to ease auditing with DSpace
"""

import argparse
import csv
import os
import pathlib


def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input_item", required=True, help="CSV file from the Jupiter Item export."
    )
    parser.add_argument(
        "--input_thesis", required=True, help="CSV file from the Jupiter Thesis export."
    )
    parser.add_argument("--output", required=True, help="CSV combined header output.")

    return parser.parse_args()


#
def process(input_item, input_thesis, output):
    """
    Main processing method
    """
    with open(input_item, "r", encoding="utf-8", newline="") as f_item:
        with open(input_thesis, "r", encoding="utf-8", newline="") as f_thesis:
            csv_item = csv.DictReader(f_item)
            csv_thesis = csv.DictReader(f_thesis)

            item_headers = csv_item.fieldnames
            thesis_headers = csv_thesis.fieldnames

            # Combing headers from both Item and Thesis, eliminate duplicates
            combined_headers = item_headers + [
                field for field in thesis_headers if field not in item_headers
            ]

            csv_output = csv.DictWriter(output, fieldnames=combined_headers)
            csv_output.writeheader()

            # For each column name / key in the header, populate a dict
            # with either the key value in the row or a "" if not present,
            # for example, a Jupiter Item will not have a thesis_level.
            # Uses a dictionary comprehension to iterate
            for row in csv_item:
                csv_output.writerow(
                    {key: row.get(key, "") for key in combined_headers}
                )

            for row in csv_thesis:
                csv_output.writerow(
                    {key: row.get(key, "") for key in combined_headers}
                )


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    pathlib.Path(os.path.dirname(args.output)).mkdir(parents=True, exist_ok=True)
    with open(args.output, "wt", encoding="utf-8", newline="") as output_file:
        process(args.input_item, args.input_thesis, output_file)


#
if __name__ == "__main__":
    main()
