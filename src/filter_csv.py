"""
Filter a CSV file given a list of IDs a flag specifying the column header name
where the IDs are located in the source CSV file. Write the filted to a new CSV file.

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
        "--input",
        required=True,
        help="Origin CSV file with a column header specified by '--column'.",
    )
    parser.add_argument(
        "--column",
        required=True,
        help="CSV header name in the origin CSV where IDs are stored for filtering.",
    )
    parser.add_argument(
        "--ids_file", required=True, help="CSV file with a list of IDs."
    )
    parser.add_argument(
        "--output", required=True, help="Location to store output file."
    )

    return parser.parse_args()


def process(input_file, column, ids_file, output_file):
    """
    Main processing method
    """

    with open(input_file, "r", encoding="utf-8", newline="") as f_input:
        with open(ids_file, "r", encoding="utf-8", newline="") as f_ids:

            csv_input = csv.DictReader(f_input)
            csv_ids = csv.DictReader(f_ids)
            csv_output = csv.DictWriter(output_file, fieldnames=csv_input.fieldnames)
            csv_output.writeheader()

            # Read IDs into a set for indexed/hashed lookup
            id_set = set()
            for row in csv_ids:
                id_set.add(row[column])

            # If ID exists in the set, write the row to the output.
            for row in csv_input:
                if row[column] in id_set:
                    csv_output.writerow(row)


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    pathlib.Path(os.path.dirname(args.output)).mkdir(parents=True, exist_ok=True)
    with open(args.output, "wt", encoding="utf-8", newline="") as output_file:
        process(args.input, args.column, args.ids_file, output_file)


#
if __name__ == "__main__":
    main()
