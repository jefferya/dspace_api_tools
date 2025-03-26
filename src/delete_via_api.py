"""
##############################################################################################
# desc: delete_via_api.py:
#     Test https://pypi.org/project/dspace-rest-client
#     to delete communities, collections, items from a DSpace instance
#     and write the output to a file.
#     https://github.com/the-library-code/dspace-rest-python/blob/main/dspace_rest_client/client.py
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: March 24, 2025
##############################################################################################
"""

import argparse
import csv
import logging
import sys

from dspace_rest_client.client import DSpaceClient

from utils import utilities as utils


def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Location of a CSV with a column named 'id' with cells of the form 'uuid'.",
    )
    parser.add_argument(
        "--logging_level", required=False, help="Logging level.", default="INFO"
    )

    return parser.parse_args()


#
def process(dspace_client, csv_reader):
    """
    Process CSV rows and call DSpace delete
    """
    for row in csv_reader:
        print(row)
        collections = dspace_client.get_collections(uuid=row["id"])
        for collection in collections:
            logging.info("%s (%s)", collection.name, collection.uuid)
            dspace_client.delete_dso(collection)


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    dspace_client = DSpaceClient(fake_user_agent=True)

    utils.configure_logging(args.logging_level)

    utils.check_required_env_vars()

    try:
        dspace_client.authenticate()
    except TypeError as e:
        logging.error("Check credentials and VPN (if applicable) [%s]", e)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8", newline="") as input_file:
        csv_reader = csv.DictReader(
            input_file,
        )
        process(dspace_client, csv_reader)


#
if __name__ == "__main__":
    main()
