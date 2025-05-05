"""
##############################################################################################
# desc: dspace_api_export.py:
#     Leverage the https://pypi.org/project/dspace-rest-client
#     to get communities, collections, items, bitstreams, and use from a DSpace instance
#     and write the output to a CSV file viat the DSpace API.
#     https://github.com/the-library-code/dspace-rest-python/blob/main/dspace_rest_client/client.py
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: March 3, 2025
##############################################################################################
"""

import argparse
import csv
import logging
import json
import os
import pathlib
import sys

# from dspace_rest_client.client import DSpaceClient
from dspace_rest_client.models import Bundle

from utils import utilities as utils
from utils.dspace_rest_client_local import DSpaceClientLocal

DSPACE_CLIENT_TOKEN_REFRESH=5

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
        help="DSpace Object Type ['communities', 'collections', 'items', 'users'].",
        default="communities",
    )
    parser.add_argument(
        "--random_sample_by_percentage",
        required=False,
        default=100,
        type=int,
        choices=range(0, 101),
        help="Trigger a random sample to speedup runtime (1-100 percent).",
    )
    parser.add_argument(
        "--logging_level", required=False, help="Logging level.", default="INFO"
    )

    return parser.parse_args()


def process_communities(dspace_client, output_file):
    """
    Process communities
    """
    communities = dspace_client.get_communities_iter()
    writer = utils.output_init(output_file, "community")
    count = 0
    for count, community in enumerate(communities, start=1):
        logging.info("%s (%s)", community.name, community.uuid)
        logging.debug("%s", community.to_json_pretty())
        utils.output_writer(community, "community", writer)
    logging.info("Count: [%d]", count)


def process_collections(dspace_client, output_file):
    """
    Process collections
    """
    collections = dspace_client.get_collections_iter()
    writer = utils.output_init(output_file, "collection")
    count = 0
    for count, collection in enumerate(collections, start=1):
        logging.info("%s (%s)", collection.name, collection.uuid)
        logging.debug("%s", collection.to_json_pretty())
        provenance = {
            "provenance.ual.jupiterId.collection": utils.get_provenance_ual_jupiter_id(
                collection, "ual.jupiterId.collection"
            ),
            "provenance.ual.jupiterId.community": utils.get_provenance_ual_jupiter_community_id(
                dspace_client, collection
            ),
        }
        utils.output_writer(collection, "collection", writer, embbed=provenance)
    logging.info("Count: [%d]", count)


def process_items(dspace_client, output_file, random_sample_by_percentage=100):
    """
    Process items
    """
    print("\n\n+++++++++++++++++++")
    print(
        "\n Items fields only included in output if explictily added to CSV dict header and JSON flattening.\n"
    )
    print("+++++++++++++++++++\n\n")
    writer = utils.output_init(output_file, "item")
    items = dspace_client.search_objects_iter(query="*:*", dso_type="item")
    count = 0
    for count, item in enumerate(items, start=1):

        # refresh auth token
        if count % DSPACE_CLIENT_TOKEN_REFRESH == 0:
            # not sure if both are needed
            dspace_client.authenticate()
            dspace_client.refresh_token()

        logging.info("%s (%s)", item.name, item.uuid)
        logging.debug("%s", item.to_json_pretty())
        if utils.include_in_random_sample(random_sample_by_percentage):
            provenance = {
                "provenance.ual.jupiterId.collection": utils.get_provenance_ual_jupiter_collection_id(
                    dspace_client, item
                ),
                "access_rights": utils.get_access_rights(dspace_client, item),
            }
            logging.debug("------ provenance %s", provenance)
            utils.output_writer(item, "item", writer, embbed=provenance)
        else:
            logging.info("Not in random sample: %s (%s)", item.name, item.uuid)
    logging.info("Count: [%d]", count)


def process_items_by_search(dspace_client, output_file):
    """
    Process items quickly using Solr / Search API
    """
    print("\n\n+++++++++++++++++++")
    print(
        "\n Items fields only included in output if explictily added to CSV dict header and JSON flattening.\n"
    )
    print("+++++++++++++++++++\n\n")
    writer = utils.output_init(output_file, "item")

    collection_iter = dspace_client.search_objects_iter(
        query="*:*", dso_type="collection"
    )
    item_count_total = 1
    for collection in collection_iter:
        logging.info("Collection %s (%s)", collection.name, collection.uuid)
        logging.debug("%s", collection.to_json_pretty())

        # server/api/discover/search/objects?query=test&embed=thumbnail&embed=item%2Fthumbnail&embed=accessStatus
        # Consider adding the collection to each item via embed as opposed to
        #    doing the above loop
        #    embeds=["accessStatus", "owningCollection"]
        items_iter = dspace_client.search_objects_iter(
            query="*:*", scope=collection.uuid, dso_type="item", embeds=["accessStatus"]
        )

        for item in items_iter:

            if item_count_total % DSPACE_CLIENT_TOKEN_REFRESH == 0:
                # not sure if both are needed
                dspace_client.authenticate()
                dspace_client.refresh_token()

            logging.info("%s (%s)", item.name, item.uuid)
            logging.debug("%s", item.to_json_pretty())

            provenance = {
                "provenance.ual.jupiterId.collection": utils.get_provenance_ual_jupiter_id(
                    collection, "ual.jupiterId.collection"
                ),
                "access_rights": item.embedded["accessStatus"]["status"],
            }

            logging.debug("------ provenance %s", provenance)
            utils.output_writer(item, "item", writer, embbed=provenance)
            item_count_total += 1

    logging.info("Count: [%d]", item_count_total)


def process_bitstreams(dspace_client, output_file, random_sample_by_percentage=100):
    """
    Process bitstreams: mainly for existence checks and bitstream checksums
    """
    writer = utils.output_init(output_file, "bitstream")
    items = dspace_client.search_objects_iter(query="*:*", dso_type="item")
    count = 0
    for count, item in enumerate(items, start=1):
        # refresh auth token
        if count % DSPACE_CLIENT_TOKEN_REFRESH == 0:
            # not sure if both are needed
            dspace_client.authenticate()
            dspace_client.refresh_token()

        if not utils.include_in_random_sample(random_sample_by_percentage):
            logging.info("Not in random sample: %s (%s)", item.name, item.uuid)
            continue

        bundles = dspace_client.get_bundles(parent=item)
        for bundle in bundles:
            bitstreams = dspace_client.get_bitstreams(bundle=bundle)
            utils.output_bitstream(item, bundle, bitstreams, writer)

    logging.info("Count: [%d]", count)


def process_bitstreams_by_search(dspace_client, output_file):
    """
    Process bitstreams: mainly for existence checks and bitstream checksums
    Use the search API in this version
    """
    writer = utils.output_init(output_file, "bitstream")
    items = dspace_client.search_objects_iter(
        query="*:*", dso_type="item", embeds=["bundles"]
    )
    count = 0
    for count, item in enumerate(items, start=1):
        logging.info("Item: %s", item.to_json_pretty())
        # refresh auth token

        if count % DSPACE_CLIENT_TOKEN_REFRESH == 0:
            # not sure if both are needed
            dspace_client.authenticate()
            dspace_client.refresh_token()

        if "bundles" in item.embedded:
            # this could be a bug in the discovery search API the need have
            # ["_embedded"]["bundles"]
            logging.info("Embed: %s", item.embedded["bundles"]["_embedded"]["bundles"])
            for bundle in item.embedded["bundles"]["_embedded"]["bundles"]:
                logging.info("Bundle: %s", bundle)
                if bundle.get("name", None) == "ORIGINAL":
                    bundle_obj = Bundle(bundle)
                    bitstreams = dspace_client.get_bitstreams(bundle=bundle_obj)
                    utils.output_bitstream(item, bundle_obj, bitstreams, writer)

    logging.info("Count items (not actual bitstreams): [%d]", count)


def process_users(dspace_client, output_file):
    """
    Process users
    """
    writer = utils.output_init(output_file, "user")
    users = dspace_client.get_users_iter()
    count = 0
    for count, user in enumerate(users, start=1):
        utils.output_writer(user, "user", writer)
        logging.debug("%s", user.to_json_pretty())
    logging.info("Count: [%d]", count)


def process_collection_stats(dspace_client, output_file):
    """
    Process collections with the number of items in each collection
    """
    csv_writer = csv.DictWriter(
        output_file,
        fieldnames=[
            "collection.uuid",
            "collection.name",
            "provenance.ual.jupiter.id",
            "count",
        ],
    )
    csv_writer.writeheader()

    collection_mapping = utils.get_collection_mapping(dspace_client)

    logging.debug("Collection Mapping: %s", json.dumps(collection_mapping, indent=2))

    # Without Solr
    # items = dspace_client.search_objects_iter(query="*:*", dso_type="item")
    # for item in items:
    #     parent_collection = item.links["owningCollection"]["href"]
    #     r_json = dspace_client.fetch_resource(url=parent_collection)
    #     collection_uuid = r_json['uuid']
    #     if collection_uuid not in collection_mapping:
    #         logging.error(f"ERROR owning collection not found for item %s", collection_uuid)
    #         collection_mapping[collection_uuid] = {
    #            'count': 1,
    #            'collection.name': "owningCollection not found",
    #            'provenance.ual.jupiter.id': None
    #            }
    #    elif 'count' not in collection_mapping[collection_uuid]:
    #        collection_mapping[collection_uuid]['count'] = 0
    #    else:
    #        collection_mapping[collection_uuid]['count'] = collection_mapping[collection_uuid]['count'] + 1
    # logging.debug("Collection Mapping: %s", collection_mapping)

    for key, value in collection_mapping.items():
        logging.debug("Collection Mapping: %s", key)
        logging.debug("Collection Mapping: %s", value)
        items_iter = dspace_client.search_objects_iter(
            query="*:*", scope=key, dso_type="item"
        )
        if items_iter:
            value["count"] = len(list(items_iter))
        if "count" not in value:
            value["count"] = 0
        csv_writer.writerow(
            {
                "collection.uuid": key,
                "collection.name": value["collection.name"],
                "provenance.ual.jupiter.id": value["provenance.ual.jupiter.id"],
                "count": value["count"],
            }
        )


#
def process(dspace_client, output_file, dso_type, random_sample_percentage):
    """
    Main processing function
    """

    match dso_type:
        case "communities":
            process_communities(dspace_client, output_file)
        case "collections":
            process_collections(dspace_client, output_file)
        case "items":
            process_items(dspace_client, output_file, random_sample_percentage)
        case "items_by_search":
            process_items_by_search(dspace_client, output_file)
        case "bitstreams":
            process_bitstreams(dspace_client, output_file, random_sample_percentage)
        case "bitstreams_by_search":
            process_bitstreams_by_search(dspace_client, output_file)
        case "users":
            process_users(dspace_client, output_file)
        case "collection_stats":
            process_collection_stats(dspace_client, output_file)
        case _:
            logging.error("Unsupported DSO Type: %s", dso_type)
            sys.exit()


#
def main():
    """
    Main entry point
    """

    args = parse_args()

    # Base class should set this as an instance variable in the constructor
    DSpaceClientLocal.ITER_PAGE_SIZE = 100
    dspace_client = DSpaceClientLocal(fake_user_agent=False)
    # don't set size over 100 otherwise a weird disconnect happens
    # between the requested page size, actual result size and # of pages
    # If 512 items and size is set to 500,
    # https://github.com/DSpace/DSpace/issues/8723
    # http://198.168.187.81:8080/server/api/discover/search/objects?dsoType=collection&page=0&size=500
    # dspace_client.ITER_PAGE_SIZE = 100

    # Configure logging
    log_level = getattr(logging, args.logging_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.log}")
    # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    logging.getLogger().setLevel(log_level)

    utils.check_required_env_vars()

    try:
        dspace_client.authenticate()
    except TypeError as e:
        logging.error(
            "Authentication error, check credentials and VPN (if applicable) [%s]", e
        )
        sys.exit(1)

    pathlib.Path(os.path.dirname(args.output)).mkdir(parents=True, exist_ok=True)
    with open(args.output, "wt", encoding="utf-8", newline="") as output_file:
        process(
            dspace_client, output_file, args.dso_type, args.random_sample_by_percentage
        )


#
if __name__ == "__main__":
    main()
