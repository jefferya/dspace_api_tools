"""
##############################################################################################
# desc: dspace_api_resource_policy.py:
#     Leverage the https://pypi.org/project/dspace-rest-client
#     to test creating a DSpace API Resoorce Policy creation script.
#     https://github.com/the-library-code/dspace-rest-python/blob/main/dspace_rest_client/client.py
# usage:
#  ./venv/bin/python src/dspace_api_resource_policy.py \
#      --item_id "8131338a-4c35-48ca-87f5-e00ca75342e9" \
#      --embargo_date 2000-01-02 --logging_level DEBUG
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: March 3, 2025
##############################################################################################
"""

import argparse
import logging
import json
import sys

from utils import utilities as utils
from utils.dspace_rest_client_local import DSpaceClientLocal

DSPACE_CLIENT_TOKEN_REFRESH = 500


def parse_args():
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--item_id",
        required=True,
        help="The DSpace ID of an Item.",
    )
    parser.add_argument(
        "--embargo_date", required=False, help="Embargo date.", default="2027-08-09"
    )
    parser.add_argument(
        "--logging_level", required=False, help="Logging level.", default="INFO"
    )

    return parser.parse_args()


def lookup_item_resource_policy(dspace_client, item_id):
    """
    Lookup resource policies for a specified item_id.
    http://localhost:8080/server/api/authz/resourcepolicies/search/resource?uuid=8131338a-4c35-48ca-87f5-e00ca75342e9
    """

    # url = "http://localhost:8080/server/api/authz/resourcepolicies/search/resource"
    url = f"{dspace_client.API_ENDPOINT}/authz/resourcepolicies/search/resource"

    # Lookup Resource Policies for a specified "item_id"
    params = {"uuid": item_id}
    response = dspace_client.api_get(url, params=params)
    resource_policy = json.loads(response.content)["_embedded"]["resourcepolicies"]
    logging.debug(
        "Resource Policies for Item %s: %s",
        item_id,
        json.dumps(resource_policy, indent=4),
    )

    return resource_policy


def update_item_resource_policy(dspace_client, item_id, resource_policy, embargo_date):
    """
    Update a resource policy for a specified item_id.
    http://localhost:8080/server/api/authz/resourcepolicies/270
    """

    # This code is based on the starting state and instructions described in this document: 
    # https://tdl-ir.tdl.org/server/api/core/bitstreams/aa922a36-e9cd-4bc6-811d-f78a230cf86d/content
    # The above document describes one starting state but I suspect there are other possible
    # starting states. The code flow is gathered from using the web UI and viewing the web request
    # when following the above documentation.
    # Assumptions:
    #     Verify "0" is always the correct index
    #     Verify that the steps described in this documentation are correct in all cases, for example,
    #     Will "edit" always be the correct workflow? What if there are multiple resource policies returned?
    #         or a preexisting resource policy?
    resource_policy_id = resource_policy[0]["id"]
    # url = f"http://localhost:8080/server/api/authz/resourcepolicies/{resource_policy_id}"
    url = f"{dspace_client.API_ENDPOINT}/authz/resourcepolicies/{resource_policy_id}"
    # params = {
    #    "name": "embargo",
    #    "policyType": "TYPE_CUSTOM",
    #    "startDate": embargo_date
    # }
    # for key, value in params.items():
    # response = dspace_client.api_patch(url, dspace_client.PatchOperation.REPLACE, f"/{key}", value)
    # logging.debug("Update %s: %s", item_id, response.content)

    # http://localhost:8080/server/api/authz/resourcepolicies/270
    # Don't use the dspace_client.api_patch here as can only update one field at a time
    # Payload from the UI when multiple fields are updated:
    # [
    #   {"op":"replace","path":"/startDate","value":"9876-01-01T00:00:00Z"},
    #   {"op":"replace","path":"/name","value":"embargo1"}
    # ]
    data = [
        {"op": "replace", "path": "/startDate", "value": embargo_date},
        {"op": "replace", "path": "/name", "value": "embargo"},
        {"op": "replace", "path": "/policyType", "value": "TYPE_CUSTOM"},
    ]
    response = dspace_client.session.patch(
        url, headers=dspace_client.request_headers, json=data
    )
    logging.debug("Update %s: %s", item_id, response.content)


def process_item_embargo(dspace_client, item_id, embargo_date):
    """
    Add resource policy to apply an embargo date to an item.
    Base on UI and these documents:
    https://tdl-ir.tdl.org/server/api/core/bitstreams/aa922a36-e9cd-4bc6-811d-f78a230cf86d/content
    https://github.com/DSpace/RestContract/blob/dspace-7_x/resourcepolicies.md
    """

    # The flow is gathered from using the web UI and viewing the web requests when following
    # the instructions for adding an embargo resource policy as described here:
    # https://tdl-ir.tdl.org/server/api/core/bitstreams/aa922a36-e9cd-4bc6-811d-f78a230cf86d/content
    resource_policy = lookup_item_resource_policy(dspace_client, item_id)
    update_item_resource_policy(dspace_client, item_id, resource_policy, embargo_date)


#
def process(dspace_client, args):
    """
    Main processing function
    """

    process_item_embargo(dspace_client, args.item_id, args.embargo_date)


#
def main():
    """
    Main entry point
    """
    # pylint: disable=R0801

    args = parse_args()

    dspace_client = DSpaceClientLocal(fake_user_agent=False)
    dspace_client.authenticate()

    # Configure logging
    utils.configure_logging(args.logging_level)

    # Check required environment variables
    utils.check_required_env_vars()

    try:
        dspace_client.authenticate()
    except TypeError as e:
        logging.error(
            "Authentication error, check credentials and VPN connection (if applicable) [%s]",
            e,
        )
        sys.exit(1)

    process(dspace_client, args)


#
if __name__ == "__main__":
    main()
