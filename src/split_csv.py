"""
Split a CSV file into "x" new files with a header row
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
        help="Origin CSV file with a row.",
    )
    parser.add_argument(
        "--output_file_size", required=True, help="Number of files to output."
    )
    parser.add_argument(
        "--output", required=True, help="Location to store output file."
    )

    return parser.parse_args()


def process(input_file, output_file_size, output_file):
    """
    Main processing method
    """

    with open(input_file, "r", encoding="utf-8", newline="") as f_input:

        # pylint: disable=consider-using-with

        csv_input = csv.DictReader(f_input)

        output_file_fd = None
        for count, row in enumerate(csv_input, start=0):

            if count % output_file_size == 0:
                if count > 0:
                    output_file_fd.close()
                output_file_name = (
                    f"{output_file}_items_{count}_to_{count+output_file_size-1}.csv"
                )
                output_file_fd = open(
                    output_file_name, "w", encoding="utf-8", newline=""
                )
                csv_output = csv.DictWriter(
                    output_file_fd, fieldnames=csv_input.fieldnames
                )
                csv_output.writeheader()

            csv_output.writerow(row)
        if output_file_fd is not None:
            output_file_fd.close()


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    pathlib.Path(os.path.dirname(args.output)).mkdir(parents=True, exist_ok=True)
    process(args.input, int(args.output_file_size), args.output)


#
if __name__ == "__main__":
    main()
