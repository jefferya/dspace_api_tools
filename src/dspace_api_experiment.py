"""
##############################################################################################
# desc: .py:
#     Experiment with the https://pypi.org/project/dspace-rest-client
#     to get communities, collections, items from a DSpace instance
#     and write the output to a file.
#     https://github.com/the-library-code/dspace-rest-python/blob/main/dspace_rest_client/client.py
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: March 3, 2025
##############################################################################################
"""

import argparse
import logging
import os
import pathlib
import sys

from dspace_rest_client.client import DSpaceClient

from utils import utilities as utils


def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output", required=True, help="Location to store output file."
    )
    parser.add_argument(
        "--dso_type",
        required=False,
        help="DSpace Object Type ['communities', 'collections', 'item'].",
        default="communities",
    )
    parser.add_argument(
        "--logging_level", required=False, help="Logging level.", default=logging.INFO
    )

    return parser.parse_args()


def check_required_env_vars():
    """
    Check if the https://pypi.org/project/dspace-rest-client
    Environment variables exist
    """
    if "DSPACE_API_ENDPOINT" not in os.environ:
        logging.error("Env Var DSPACE_API_ENDPOINT not set, exiting.")
        sys.exit()
    if "DSPACE_API_USERNAME" not in os.environ:
        logging.error("Env Var DSPACE_API_USERNAME not set, exiting.")
        sys.exit()
    if "DSPACE_API_PASSWORD" not in os.environ:
        logging.error("Env Var DSPACE_API_PASSWORD not set, exiting.")
        sys.exit()


def process_communities(dspace_client, output_file):
    """
    Process communities
    """
    communities = dspace_client.get_communities_iter()
    writer = utils.output_init(output_file, utils.CSV_FLATTENED_HEADERS["community"])
    count = 0
    for count, community in enumerate(communities, start=1):
        utils.output_writer(community, writer)
        logging.info("%s (%s)", community.name, community.uuid)
        logging.debug("%s", community.to_json_pretty())
    logging.info("Count: [%d]", count)


def process_collections(dspace_client, output_file):
    """
    Process collections
    """
    collections = dspace_client.get_collections_iter()
    writer = utils.output_init(output_file, utils.CSV_FLATTENED_HEADERS["collections"])
    count = 0
    for count, collection in enumerate(collections, start=1):
        utils.output_writer(collection, writer)
        logging.info("%s (%s)", collection.name, collection.uuid)
        logging.debug("%s", collection.to_json_pretty())
    logging.info("Count: [%d]", count)


def process_items(dspace_client, output_file):
    """
    Process items
    """
    print("\n\n+++++++++++++++++++")
    print("\n Items will likely fail due to CSV dict header and JSON flattening.\n")
    print("+++++++++++++++++++\n\n")
    writer = utils.output_init(output_file, utils.CSV_FLATTENED_HEADERS["items"])
    items = dspace_client.search_objects_iter(query="*:*", dso_type="item")
    count = 0
    for count, item in enumerate(items, start=1):
        item_expanded = {**item.as_dict(), "bundles": []}
        # refresh auth token
        if count % 5000 == 0:
            dspace_client.refresh_token()
        logging.debug("%s", item.to_json_pretty())
        bundles = dspace_client.get_bundles(parent=item)
        logging.debug("%s A --------------------------------------------", item.uuid)
        for bundle in bundles:
            logging.debug(
                "%s B --------------------------------------------", bundle.uuid
            )
            logging.debug("%s", bundle.to_json_pretty())
            bundle_expanded = {**bundle.as_dict(), "bitstreams": []}
            bitstreams = dspace_client.get_bitstreams(bundle=bundle)
            for bitstream in bitstreams:
                bundle_expanded["bitstreams"].append(bitstream.as_dict())
                logging.debug("%s", bitstream.to_json_pretty())
            item_expanded["bundles"].append(bundle_expanded)
        utils.output_writer(item_expanded, writer)
    logging.info("Count: [%d]", count)


def process_users(dspace_client, output_file):
    """
    Process users
    """
    writer = utils.output_init(output_file, utils.CSV_FLATTENED_HEADERS["users"])
    users = dspace_client.get_users_iter()
    count = 0
    for count, user in enumerate(users, start=1):
        utils.output_writer(user, writer)
        logging.debug("%s", user.to_json_pretty())
    logging.info("Count: [%d]", count)


#
def process(dspace_client, output_file, dso_type):
    """
    Main processing function
    """

    match dso_type:
        case "communities":
            process_communities(dspace_client, output_file)
        case "collections":
            process_collections(dspace_client, output_file)
        case "items":
            process_items(dspace_client, output_file)
        case "users":
            process_users(dspace_client, output_file)
        case _:
            logging.error("Unsupported DSO Type: %s", dso_type)
            sys.exit()


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    dspace_client = DSpaceClient(fake_user_agent=True)

    # Configure logging
    log_level = getattr(logging, args.logging_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.log}")
    # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    logging.getLogger().setLevel(log_level)

    check_required_env_vars()

    if not dspace_client.authenticate():
        logging.error("Authentication error, exiting")
        sys.exit()

    pathlib.Path(os.path.dirname(args.output)).mkdir(parents=True, exist_ok=True)
    with open(args.output, "wt", encoding="utf-8", newline="") as output_file:
        process(dspace_client, output_file, args.dso_type)


#
if __name__ == "__main__":
    main()
