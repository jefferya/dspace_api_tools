"""
Script utility functions
"""

import ast
import csv
import logging
import json
import os
import sys


# The CSV_HEADERS dictionary is used to define the headers for the CSV file
# The keys are the DSpace object types and the values are from the Flattened JSON object
CSV_FLATTENED_HEADERS = {
    "community": [
        "uuid",
        "name",
        "handle",
        "metadata",
        "lastModified",
        "type",
        "metadata.dc.description",
        "metadata.dc.description.abstract",
        "metadata.dc.identifier.uri",
        "metadata.dc.rights",
        "metadata.dc.title",
    ],
    "collection": [
        "handle",
        "name",
        "lastModified",
        "type",
        "uuid",
        "provenance.ual.jupiterId.collection",
        "provenance.ual.jupiterId.community",
        "metadata.dc.description",
        "metadata.dc.description.abstract",
        "metadata.dc.identifier.uri",
        "metadata.dc.provenance.0.authority",
        "metadata.dc.provenance.0.confidence",
        "metadata.dc.provenance.0.language",
        "metadata.dc.provenance.0.place",
        "metadata.dc.provenance.0.value",
        "metadata.dc.title",
        "metadata.dspace.entity.type",
    ],
    "item": [
        "uuid",
        "metadata.ual.jupiterId",
        "handle",
        "lastModified",
        "name",
        "provenance.ual.jupiterId.item",
        "provenance.ual.jupiterId.collection",
        "type",
        "access_rights",
        "metadata.dc.contributor",
        "metadata.dc.contributor.author",
        "metadata.dc.contributor.advisor",
        "metadata.dc.contributor.other",
        "metadata.dc.coverage.spatial",
        "metadata.dc.coverage.temporal",
        "metadata.dc.creator",
        "metadata.dc.date.accessioned",
        "metadata.dc.date.available",
        "metadata.dc.date.created",
        "metadata.dc.date.issued",
        "metadata.dc.description",
        "metadata.dc.description.abstract",
        "metadata.dc.description.provenance",
        "metadata.dc.description.sponsorship",
        "metadata.dc.identifier.citation",
        "metadata.dc.identifier.govdoc",
        "metadata.dc.identifier.isbn",
        "metadata.dc.identifier.ismn",
        "metadata.dc.identifier.issn",
        "metadata.dc.identifier.other",
        "metadata.dc.identifier.doi",
        "metadata.dc.identifier.uri",
        "metadata.dc.language",
        "metadata.dc.language.iso",
        "metadata.dc.publisher",
        "metadata.dc.relation",
        "metadata.dc.relation.isversionof",
        "metadata.dc.relation.ispartof",
        "metadata.dc.relation.ispartofseries",
        "metadata.dc.rights",
        "metadata.dc.rights.license",
        "metadata.dc.source",
        "metadata.dc.subject",
        "metadata.dc.title",
        "metadata.dc.title.alternative",
        "metadata.dc.type",
        "metadata.dcterms.accessRights",
        "metadata.dcterms.available",
        "metadata.dcterms.source",
        "metadata.dspace.entity.type",
        "metadata.local.embargo.lift",
        "metadata.local.embargo.terms",
        "metadata.person.email",
        "metadata.person.familyName",
        "metadata.person.givenName",
        "metadata.relation.isAuthorOfPublication",
        "metadata.relation.isAuthorOfPublication.latestForDiscovery",
        "metadata.relation.isPublicationOfAuthor",
        "metadata.relation.isPublicationOfAuthor.latestForDiscovery",
        "metadata.thesis.degree.discipline",
        "metadata.thesis.degree.grantor",
        "metadata.thesis.degree.level",
        "metadata.thesis.degree.name",
        "metadata.ual.date.createdInERA",
        "metadata.ual.date.createdInJupiter",
        "metadata.ual.date.graduation",
        "metadata.ual.date.updatedInJupiter",
        "metadata.ual.department",
        "metadata.ual.depositor",
        "metadata.ual.fedora3Handle",
        "metadata.ual.fedora3UUID",
        "metadata.ual.jupiterCollection",
        "metadata.ual.jupiterFilename",
        "metadata.ual.jupiterId",
        "metadata.ual.jupiterThumbnail",
        "metadata.ual.hydraNoid",
        "metadata.ual.ingestBatch",
        "metadata.ual.owner",
        "metadata.ual.recordCreatedInJupiter",
        "metadata.ual.sortYear",
        "metadata.ual.stats.jupiterDownloads",
        "metadata.ual.stats.jupiterViews",
    ],
    "bitstream": [
        "item.handle",
        "item.uuid",
        "item.name",
        "provenance.ual.jupiterId.item",
        "bitstream.bundleName",
        "bitstream.sizeBytes",
        "bitstream.id",
        "bitstream.name",
        "bitstream.sequenceId",
        "bitstream.checksum.value",
        "bitstream.checksum_algorithm",
        "bitstream.uuid",
        "bitstream.metadata.dc.title",
        "bitstream.metadata.dc.source.0.value",
        "bitstream.metadata.dc.description",
        "bundle.name",
    ],
    "user": [
        "canLogIn",
        "email",
        "handle",
        "lastActive",
        "lastModified",
        "name",
        "netid",
        "requireCertificate",
        "selfRegistered",
        "type",
        "uuid",
        "metadata.dspace.agreements.cookies.0.authority",
        "metadata.dspace.agreements.cookies.0.confidence",
        "metadata.dspace.agreements.cookies.0.language",
        "metadata.dspace.agreements.cookies.0.place",
        "metadata.dspace.agreements.cookies.0.value",
        "metadata.dspace.agreements.end-user.0.value",
        "metadata.dspace.agreements.end-user.0.confidence",
        "metadata.dspace.agreements.end-user.0.language",
        "metadata.dspace.agreements.end-user.0.place",
        "metadata.dspace.agreements.end-user.0.authority",
        "metadata.eperson.firstname.0.authority",
        "metadata.eperson.firstname.0.confidence",
        "metadata.eperson.firstname.0.language",
        "metadata.eperson.firstname.0.place",
        "metadata.eperson.firstname.0.value",
        "metadata.eperson.language.0.authority",
        "metadata.eperson.language.0.confidence",
        "metadata.eperson.language.0.language",
        "metadata.eperson.language.0.value",
        "metadata.eperson.language.0.place",
        "metadata.eperson.lastname.0.authority",
        "metadata.eperson.lastname.0.confidence",
        "metadata.eperson.lastname.0.language",
        "metadata.eperson.lastname.0.place",
        "metadata.eperson.lastname.0.value",
    ],
}

# Deconstruct the JSON structure from the DSpace API and extract out the values
# during the JSON flattening into a list of values
#
fields_deconstruct_to_list_of_values = [
    "dc.contributor",
    "dc.contributor.advisor",
    "dc.contributor.author",
    "dc.contributor.other",
    "dc.coverage.spatial",
    "dc.coverage.temporal",
    "dc.creator",
    "dc.date.accessioned",
    "dc.date.available",
    "dc.date.created",
    "dc.date.issued",
    "dc.description",
    "dc.description.abstract",
    "dc.description.provenance",
    "dc.description.sponsorship",
    "dc.identifier.citation",
    "dc.identifier.govdoc",
    "dc.identifier.isbn",
    "dc.identifier.ismn",
    "dc.identifier.issn",
    "dc.identifier.other",
    "dc.identifier.doi",
    "dc.identifier.uri",
    "dc.language",
    "dc.language.iso",
    "dc.publisher",
    "dc.relation",
    "dc.relation.isversionof",
    "dc.relation.ispartof",
    "dc.relation.ispartofseries",
    "dc.rights",
    "dc.rights.license",
    "dc.source",
    "dc.subject",
    "dc.title",
    "dc.title.alternative",
    "dc.type",
    "dcterms.accessRights",
    "dcterms.available",
    "dcterms.source",
    "dspace.entity.type",
    "local.embargo.lift",
    "local.embargo.terms",
    "person.email",
    "person.familyName",
    "person.givenName",
    "relation.isAuthorOfPublication",
    "relation.isAuthorOfPublication.latestForDiscovery",
    "relation.isPublicationOfAuthor",
    "relation.isPublicationOfAuthor.latestForDiscovery",
    "thesis.degree.discipline",
    "thesis.degree.grantor",
    "thesis.degree.level",
    "thesis.degree.name",
    "ual.date.createdInERA",
    "ual.date.createdInJupiter",
    "ual.date.graduation",
    "ual.date.updatedInJupiter",
    "ual.department",
    "ual.depositor",
    "ual.fedora3Handle",
    "ual.fedora3UUID",
    "ual.jupiterCollection",
    "ual.jupiterFilename",
    "ual.jupiterThumbnail",
    "ual.hydraNoid",
    "ual.ingestBatch",
    "ual.owner",
    "ual.recordCreatedInJupiter",
    "ual.sortYear",
    "ual.stats.jupiterDownloads",
    "ual.stats.jupiterViews",
    "provenance.ual.jupiterId.item",
    # "provenance.ual.jupiterId.collection",
]

# Deconstruct the JSON structure from the DSpace API and extract out the values
# during the JSON flattening into a single value
# For example
#
fields_deconstruct_to_a_single_value = ["ual.jupiterId"]


def deconstruct_list_of_dicts_to_list_of_values(list_of_dicts):
    """
    Deconstruct a list of dictionaries to a list of values
    """
    return [item["value"] for item in list_of_dicts]


def deconstruct_list_of_dicts_to_a_single_value(list_of_dicts):
    """
    Deconstruct a list of dictionaries to a single value
    Example, we only want the "value":
        "dc.contributor.author" : [ {
        "value" : "Item - Test Creator 1",
        "language" : null,
        "authority" : null,
        "confidence" : -1,
        "place" : 0
        }
    """
    return list_of_dicts[0]["value"]


def deconstruct_list_of_non_dicts_to_list_of_values(
    value, flat_dict, flat_key, flattened_schema
):
    """
    Deconstruct a list of non-dict structures into a list of values
    """
    for i, item in enumerate(value):
        if item is not None and isinstance(item, dict):
            flat_dict.update(flatten_json(item, flattened_schema, f"{flat_key}.{i}."))
        else:
            if flat_key in flattened_schema:
                flat_dict.setdefault(flat_key, []).append(item)
            else:
                if (
                    flat_key.startswith(tuple(fields_deconstruct_to_list_of_values))
                ) is False:
                    logging.info("Key not found in schema [list]: %s", flat_key)


def flatten_json(json_obj, flattened_schema, prefix=""):
    """
    Flatten JSON object in a very naive way for use in a CSV serialization.
    DSpace Items likely require a more complex flattening to generate "useful" output.
    """
    if isinstance(json_obj, dict) is False:
        logging.error("Failure to parse [%s] %s", prefix, json_obj)
    flat_dict = {}
    for key, value in json_obj.items():
        flat_key = f"{prefix}{key}"
        if isinstance(value, dict):
            flat_dict.update(flatten_json(value, flattened_schema, f"{prefix}{key}."))
        elif isinstance(value, list) and key in fields_deconstruct_to_a_single_value:
            flat_dict[flat_key] = deconstruct_list_of_dicts_to_a_single_value(value)
            logging.debug(
                "Deconstructed list of dict: %s - %s", flat_key, flat_dict[flat_key]
            )
        elif isinstance(value, list) and key in fields_deconstruct_to_list_of_values:
            flat_dict[flat_key] = deconstruct_list_of_dicts_to_list_of_values(value)
            logging.debug(
                "Deconstructed list of dict: %s - %s", flat_key, flat_dict[flat_key]
            )
        elif isinstance(value, list):
            deconstruct_list_of_non_dicts_to_list_of_values(
                value, flat_dict, flat_key, flattened_schema
            )
        else:
            if flat_key in flattened_schema:
                flat_dict[flat_key] = value
            else:
                logging.info("Key not found in schema [not list member]: %s", flat_key)

    return flat_dict


def output_init(output_file, dso_type=None, output_type="csv"):
    """
    Output initialization and
    """
    if output_type == "csv":
        # writer = csv.DictWriter(output_file, fieldnames= .as_dict[0].keys())
        writer = csv.DictWriter(output_file, fieldnames=CSV_FLATTENED_HEADERS[dso_type])
        writer.writeheader()
    return writer


def output_writer(dso, dso_type, writer, output_type="csv", embbed=None):
    """
    Output the specified DSpace object (dso)
    """
    if output_type == "csv":
        dso_dict = dso.as_dict() if hasattr(dso, "as_dict") else dso
        dso_dict = dso_dict | embbed if embbed else dso_dict
        writer.writerow(flatten_json(dso_dict, CSV_FLATTENED_HEADERS[dso_type]))
    elif output_type == "json":
        # fails: not valid json when combined print(dso.to_json_pretty())
        sys.exit()
    else:
        logging.error("Unsupported output type: %s", output_type)
        sys.exit()


def get_provenance_ual_jupiter_id(dso, key):
    """
    Get the DC provenance UAL Jupiter ID from the collection
    """
    dc_provenance_ual_jupiter_id = None
    if "dc.provenance" in dso.metadata:
        for provenance in dso.metadata["dc.provenance"]:
            if provenance["value"] != "":
                provenance_json = convert_string_to_json(provenance["value"])
                dc_provenance_ual_jupiter_id = (
                    provenance_json.get(key) if provenance_json else None
                )
    return dc_provenance_ual_jupiter_id


def convert_string_to_json(string):
    """
    Convert a string to a JSON object
    """
    try:
        return json.loads(string)
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON string: [%s] error %s", string, e)
        return None


def convert_string_list_representation_to_list(string):
    """
    Convert a string representation of a list (e.g., "['a','b']") to a list
    """
    # try:
    #    return json.loads(string) if isinstance(string, str) and string != '' else []
    # except json.JSONDecodeError as e:
    #    logging.error("Error decoding JSON string: [%s] error %s", string, e)
    #    return None
    try:
        return (
            ast.literal_eval(string) if isinstance(string, str) and string != "" else []
        )
    except ValueError as e:
        logging.error("Error decoding JSON string: [%s] error %s", string, e)
        return None


def get_provenance_ual_jupiter_community_id(dspace_client, collection):
    """
    Get the DC provenance UAL Jupiter ID from the collection
    """
    parent_community = collection.links["parentCommunity"]["href"]
    r_json = dspace_client.fetch_resource(url=parent_community)
    # Currently, the parent community doesn't have provenance metadata
    #   thus use "name"
    return r_json["name"]


def get_provenance_ual_jupiter_collection_id(dspace_client, item):
    """
    Get the DC provenance UAL Jupiter ID from the Collection
    assocated with the Item
    """
    # Should mapped collections be included?
    # parent_community = item.links["mappedCollections"]["href"]
    parent_community = item.links["owningCollection"]["href"]
    r_json = dspace_client.fetch_resource(url=parent_community)
    collections = dspace_client.get_collections(uuid=r_json["uuid"])
    ret = []
    for c in collections:
        ret.append(get_provenance_ual_jupiter_id(c, "ual.jupiterId.collection"))
    return ret


def get_access_rights(dspace_client, item):
    """
    Get the access rights assocated with the Item
    """
    access_rights_href = item.links["accessStatus"]["href"]
    r_json = dspace_client.fetch_resource(url=access_rights_href)
    return r_json["status"]


def get_collection_mapping(dspace_client):
    """
    Get the collection mapping
    """
    collection_iter = dspace_client.search_objects_iter(
        query="*:*", dso_type="collection"
    )
    collection_mapping = {}
    for collection in collection_iter:
        collection_mapping[collection.uuid] = {
            "collection.name": collection.name,
            "provenance.ual.jupiter.id": get_provenance_ual_jupiter_id(
                collection, "ual.jupiterId.collection"
            ),
            # "collection.url": collection.links["self"]["href"]
        }
    return collection_mapping


def get_items_given_collection_id(dspace_client, collection_id):
    """
    Get the items given a collection ID
    """
    items = dspace_client.search_objects_iter(
        query="*:*", scope=collection_id, dso_type="item"
    )

    return items


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


# Configure logging
def configure_logging(logging_level):
    """
    Set logging level
    """
    log_level = getattr(logging, logging_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {logging_level}")
    # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    logging.getLogger().setLevel(log_level)
