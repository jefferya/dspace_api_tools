"""
Script utility functions
"""

import csv
import logging
import json
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
        "metadata.dc.description.0.authority",
        "metadata.dc.description.0.confidence",
        "metadata.dc.description.0.language",
        "metadata.dc.description.0.place",
        "metadata.dc.description.0.value",
        "metadata.dc.description.abstract.0.authority",
        "metadata.dc.description.abstract.0.confidence",
        "metadata.dc.description.abstract.0.language",
        "metadata.dc.description.abstract.0.place",
        "metadata.dc.description.abstract.0.value",
        "metadata.dc.identifier.uri.0.authority",
        "metadata.dc.identifier.uri.0.confidence",
        "metadata.dc.identifier.uri.0.language",
        "metadata.dc.identifier.uri.0.place",
        "metadata.dc.identifier.uri.0.value",
        "metadata.dc.title.0.authority",
        "metadata.dc.title.0.confidence",
        "metadata.dc.title.0.language",
        "metadata.dc.title.0.place",
        "metadata.dc.title.0.value",
    ],
    "collection": [
        "handle",
        "name",
        "lastModified",
        "type",
        "uuid",
        "provenance.ual.jupiterId.collection",
        "provenance.ual.jupiterId.community",
        "metadata.dc.description.abstract.0.authority",
        "metadata.dc.description.abstract.0.confidence",
        "metadata.dc.description.abstract.0.language",
        "metadata.dc.description.abstract.0.place",
        "metadata.dc.description.abstract.0.value",
        "metadata.dc.identifier.uri.0.authority",
        "metadata.dc.identifier.uri.0.confidence",
        "metadata.dc.identifier.uri.0.language",
        "metadata.dc.identifier.uri.0.place",
        "metadata.dc.identifier.uri.0.value",
        "metadata.dc.provenance.0.authority",
        "metadata.dc.provenance.0.confidence",
        "metadata.dc.provenance.0.language",
        "metadata.dc.provenance.0.place",
        "metadata.dc.provenance.0.value",
        "metadata.dc.title.0.authority",
        "metadata.dc.title.0.confidence",
        "metadata.dc.title.0.language",
        "metadata.dc.title.0.place",
        "metadata.dc.title.0.value",
        "metadata.dc.description.0.authority",
        "metadata.dc.description.0.value",
        "metadata.dc.description.0.confidence",
        "metadata.dc.description.0.language",
        "metadata.dc.description.0.place",
    ],
    "item": [
        "handle",
        "lastModified",
        "metadata.dc.contributor.author.0.authority",
        "metadata.dc.contributor.author.0.confidence",
        "metadata.dc.contributor.author.0.language",
        "metadata.dc.contributor.author.0.place",
        "metadata.dc.contributor.author.0.value",
        "metadata.dc.contributor.author.1.authority",
        "metadata.dc.contributor.author.1.confidence",
        "metadata.dc.contributor.author.1.language",
        "metadata.dc.contributor.author.1.place",
        "metadata.dc.contributor.author.1.value",
        "metadata.dc.contributor.author.2.authority",
        "metadata.dc.contributor.author.2.confidence",
        "metadata.dc.contributor.author.2.language",
        "metadata.dc.contributor.author.2.place",
        "metadata.dc.contributor.author.2.value",
        "metadata.dc.contributor.other.0.authority",
        "metadata.dc.contributor.other.0.confidence",
        "metadata.dc.contributor.other.0.language",
        "metadata.dc.contributor.other.0.place",
        "metadata.dc.contributor.other.0.value",
        "metadata.dc.contributor.other.1.authority",
        "metadata.dc.contributor.other.1.confidence",
        "metadata.dc.contributor.other.1.language",
        "metadata.dc.contributor.other.1.place",
        "metadata.dc.contributor.other.1.value",
        "metadata.dc.contributor.other.2.authority",
        "metadata.dc.contributor.other.2.confidence",
        "metadata.dc.contributor.other.2.language",
        "metadata.dc.contributor.other.2.place",
        "metadata.dc.contributor.other.2.value",
        "metadata.dc.coverage.spatial.0.authority",
        "metadata.dc.coverage.spatial.0.confidence",
        "metadata.dc.coverage.spatial.0.language",
        "metadata.dc.coverage.spatial.0.place",
        "metadata.dc.coverage.spatial.0.value",
        "metadata.dc.coverage.spatial.1.authority",
        "metadata.dc.coverage.spatial.1.confidence",
        "metadata.dc.coverage.spatial.1.language",
        "metadata.dc.coverage.spatial.1.place",
        "metadata.dc.coverage.spatial.1.value",
        "metadata.dc.coverage.spatial.2.authority",
        "metadata.dc.coverage.spatial.2.confidence",
        "metadata.dc.coverage.spatial.2.language",
        "metadata.dc.coverage.spatial.2.place",
        "metadata.dc.coverage.spatial.2.value",
        "metadata.dc.coverage.temporal.0.authority",
        "metadata.dc.coverage.temporal.0.confidence",
        "metadata.dc.coverage.temporal.0.language",
        "metadata.dc.coverage.temporal.0.place",
        "metadata.dc.coverage.temporal.0.value",
        "metadata.dc.coverage.temporal.1.authority",
        "metadata.dc.coverage.temporal.1.confidence",
        "metadata.dc.coverage.temporal.1.language",
        "metadata.dc.coverage.temporal.1.place",
        "metadata.dc.coverage.temporal.1.value",
        "metadata.dc.coverage.temporal.2.authority",
        "metadata.dc.coverage.temporal.2.confidence",
        "metadata.dc.coverage.temporal.2.language",
        "metadata.dc.coverage.temporal.2.place",
        "metadata.dc.coverage.temporal.2.value",
        "metadata.dc.date.accessioned.0.authority",
        "metadata.dc.date.accessioned.0.confidence",
        "metadata.dc.date.accessioned.0.language",
        "metadata.dc.date.accessioned.0.place",
        "metadata.dc.date.accessioned.0.value",
        "metadata.dc.date.accessioned.1.authority",
        "metadata.dc.date.accessioned.1.confidence",
        "metadata.dc.date.accessioned.1.language",
        "metadata.dc.date.accessioned.1.place",
        "metadata.dc.date.accessioned.1.value",
        "metadata.dc.date.available.0.authority",
        "metadata.dc.date.available.0.confidence",
        "metadata.dc.date.available.0.language",
        "metadata.dc.date.available.0.place",
        "metadata.dc.date.available.0.value",
        "metadata.dc.date.available.1.authority",
        "metadata.dc.date.available.1.confidence",
        "metadata.dc.date.available.1.language",
        "metadata.dc.date.available.1.place",
        "metadata.dc.date.available.1.value",
        "metadata.dc.date.issued.0.authority",
        "metadata.dc.date.issued.0.confidence",
        "metadata.dc.date.issued.0.language",
        "metadata.dc.date.issued.0.place",
        "metadata.dc.date.issued.0.value",
        "metadata.dc.description.0.authority",
        "metadata.dc.description.0.confidence",
        "metadata.dc.description.0.language",
        "metadata.dc.description.0.place",
        "metadata.dc.description.0.value",
        "metadata.dc.description.provenance.0.authority",
        "metadata.dc.description.provenance.0.confidence",
        "metadata.dc.description.provenance.0.language",
        "metadata.dc.description.provenance.0.place",
        "metadata.dc.description.provenance.0.value",
        "metadata.dc.description.provenance.1.authority",
        "metadata.dc.description.provenance.1.confidence",
        "metadata.dc.description.provenance.1.language",
        "metadata.dc.description.provenance.1.place",
        "metadata.dc.description.provenance.1.value",
        "metadata.dc.description.provenance.2.authority",
        "metadata.dc.description.provenance.2.confidence",
        "metadata.dc.description.provenance.2.language",
        "metadata.dc.description.provenance.2.place",
        "metadata.dc.description.provenance.2.value",
        "metadata.dc.description.provenance.3.authority",
        "metadata.dc.description.provenance.3.confidence",
        "metadata.dc.description.provenance.3.language",
        "metadata.dc.description.provenance.3.place",
        "metadata.dc.description.provenance.3.value",
        "metadata.dc.identifier.doi.0.authority",
        "metadata.dc.identifier.doi.0.confidence",
        "metadata.dc.identifier.doi.0.language",
        "metadata.dc.identifier.doi.0.place",
        "metadata.dc.identifier.doi.0.value",
        "metadata.dc.identifier.uri.0.authority",
        "metadata.dc.identifier.uri.0.confidence",
        "metadata.dc.identifier.uri.0.language",
        "metadata.dc.identifier.uri.0.place",
        "metadata.dc.identifier.uri.0.value",
        "metadata.dc.language.iso.0.authority",
        "metadata.dc.language.iso.0.confidence",
        "metadata.dc.language.iso.0.language",
        "metadata.dc.language.iso.0.place",
        "metadata.dc.language.iso.0.value",
        "metadata.dc.language.iso.1.authority",
        "metadata.dc.language.iso.1.confidence",
        "metadata.dc.language.iso.1.language",
        "metadata.dc.language.iso.1.place",
        "metadata.dc.language.iso.1.value",
        "metadata.dc.language.iso.2.authority",
        "metadata.dc.language.iso.2.confidence",
        "metadata.dc.language.iso.2.language",
        "metadata.dc.language.iso.2.place",
        "metadata.dc.language.iso.2.value",
        "metadata.dc.language.iso.3.authority",
        "metadata.dc.language.iso.3.confidence",
        "metadata.dc.language.iso.3.language",
        "metadata.dc.language.iso.3.place",
        "metadata.dc.language.iso.3.value",
        "metadata.dc.relation.0.authority",
        "metadata.dc.relation.0.confidence",
        "metadata.dc.relation.0.language",
        "metadata.dc.relation.0.place",
        "metadata.dc.relation.0.value",
        "metadata.dc.relation.isversionof.0.authority",
        "metadata.dc.relation.isversionof.0.confidence",
        "metadata.dc.relation.isversionof.0.language",
        "metadata.dc.relation.isversionof.0.place",
        "metadata.dc.relation.isversionof.0.value",
        "metadata.dc.relation.isversionof.1.authority",
        "metadata.dc.relation.isversionof.1.confidence",
        "metadata.dc.relation.isversionof.1.language",
        "metadata.dc.relation.isversionof.1.place",
        "metadata.dc.relation.isversionof.1.value",
        "metadata.dc.relation.isversionof.2.authority",
        "metadata.dc.relation.isversionof.2.confidence",
        "metadata.dc.relation.isversionof.2.language",
        "metadata.dc.relation.isversionof.2.place",
        "metadata.dc.relation.isversionof.2.value",
        "metadata.dc.rights.0.authority",
        "metadata.dc.rights.0.confidence",
        "metadata.dc.rights.0.language",
        "metadata.dc.rights.0.place",
        "metadata.dc.rights.0.value",
        "metadata.dc.rights.license.0.authority",
        "metadata.dc.rights.license.0.confidence",
        "metadata.dc.rights.license.0.language",
        "metadata.dc.rights.license.0.place",
        "metadata.dc.rights.license.0.value",
        "metadata.dc.subject.0.authority",
        "metadata.dc.subject.0.confidence",
        "metadata.dc.subject.0.language",
        "metadata.dc.subject.0.place",
        "metadata.dc.subject.0.value",
        "metadata.dc.subject.1.authority",
        "metadata.dc.subject.1.confidence",
        "metadata.dc.subject.1.language",
        "metadata.dc.subject.1.place",
        "metadata.dc.subject.1.value",
        "metadata.dc.subject.2.authority",
        "metadata.dc.subject.2.confidence",
        "metadata.dc.subject.2.language",
        "metadata.dc.subject.2.place",
        "metadata.dc.subject.2.value",
        "metadata.dcterms.accessRights.0.authority",
        "metadata.dcterms.accessRights.0.confidence",
        "metadata.dcterms.accessRights.0.language",
        "metadata.dcterms.accessRights.0.place",
        "metadata.dcterms.accessRights.0.value",
        "metadata.dcterms.source.0.authority",
        "metadata.dcterms.source.0.confidence",
        "metadata.dcterms.source.0.language",
        "metadata.dcterms.source.0.place",
        "metadata.dcterms.source.0.value",
        "metadata.dc.title.0.authority",
        "metadata.dc.title.0.confidence",
        "metadata.dc.title.0.language",
        "metadata.dc.title.0.place",
        "metadata.dc.title.0.value",
        "metadata.dc.title.alternative.0.authority",
        "metadata.dc.title.alternative.0.confidence",
        "metadata.dc.title.alternative.0.language",
        "metadata.dc.title.alternative.0.place",
        "metadata.dc.title.alternative.0.value",
        "metadata.dc.type.0.authority",
        "metadata.dc.type.0.confidence",
        "metadata.dc.type.0.language",
        "metadata.dc.type.0.place",
        "metadata.dc.type.0.value",
        "metadata.local.embargo.lift.0.authority",
        "metadata.local.embargo.lift.0.confidence",
        "metadata.local.embargo.lift.0.language",
        "metadata.local.embargo.lift.0.place",
        "metadata.local.embargo.lift.0.value",
        "metadata.local.embargo.terms.0.authority",
        "metadata.local.embargo.terms.0.confidence",
        "metadata.local.embargo.terms.0.language",
        "metadata.local.embargo.terms.0.place",
        "metadata.local.embargo.terms.0.value",
        "metadata.ual.date.createdInERA.0.authority",
        "metadata.ual.date.createdInERA.0.confidence",
        "metadata.ual.date.createdInERA.0.language",
        "metadata.ual.date.createdInERA.0.place",
        "metadata.ual.date.createdInERA.0.value",
        "metadata.ual.date.createdInJupiter.0.authority",
        "metadata.ual.date.createdInJupiter.0.confidence",
        "metadata.ual.date.createdInJupiter.0.language",
        "metadata.ual.date.createdInJupiter.0.place",
        "metadata.ual.date.createdInJupiter.0.value",
        "metadata.ual.date.updatedInJupiter.0.authority",
        "metadata.ual.date.updatedInJupiter.0.confidence",
        "metadata.ual.date.updatedInJupiter.0.language",
        "metadata.ual.date.updatedInJupiter.0.place",
        "metadata.ual.date.updatedInJupiter.0.value",
        "metadata.ual.jupiterCollection.0.authority",
        "metadata.ual.jupiterCollection.0.confidence",
        "metadata.ual.jupiterCollection.0.language",
        "metadata.ual.jupiterCollection.0.place",
        "metadata.ual.jupiterCollection.0.value",
        "metadata.ual.jupiterFilename.0.authority",
        "metadata.ual.jupiterFilename.0.confidence",
        "metadata.ual.jupiterFilename.0.language",
        "metadata.ual.jupiterFilename.0.place",
        "metadata.ual.jupiterFilename.0.value",
        "metadata.ual.jupiterFilename.1.authority",
        "metadata.ual.jupiterFilename.1.confidence",
        "metadata.ual.jupiterFilename.1.language",
        "metadata.ual.jupiterFilename.1.place",
        "metadata.ual.jupiterFilename.1.value",
        "metadata.ual.jupiterFilename.2.authority",
        "metadata.ual.jupiterFilename.2.confidence",
        "metadata.ual.jupiterFilename.2.language",
        "metadata.ual.jupiterFilename.2.place",
        "metadata.ual.jupiterFilename.2.value",
        "metadata.ual.jupiterId.0.authority",
        "metadata.ual.jupiterId.0.confidence",
        "metadata.ual.jupiterId.0.language",
        "metadata.ual.jupiterId.0.place",
        "metadata.ual.jupiterId.0.value",
        "metadata.ual.jupiterThumbnail.0.authority",
        "metadata.ual.jupiterThumbnail.0.confidence",
        "metadata.ual.jupiterThumbnail.0.language",
        "metadata.ual.jupiterThumbnail.0.place",
        "metadata.ual.jupiterThumbnail.0.value",
        "metadata.ual.owner.0.authority",
        "metadata.ual.owner.0.confidence",
        "metadata.ual.owner.0.language",
        "metadata.ual.owner.0.place",
        "metadata.ual.owner.0.value",
        "metadata.ual.stats.jupiterDownloads.0.authority",
        "metadata.ual.stats.jupiterDownloads.0.confidence",
        "metadata.ual.stats.jupiterDownloads.0.language",
        "metadata.ual.stats.jupiterDownloads.0.place",
        "metadata.ual.stats.jupiterDownloads.0.value",
        "metadata.ual.stats.jupiterViews.0.authority",
        "metadata.ual.stats.jupiterViews.0.confidence",
        "metadata.ual.stats.jupiterViews.0.language",
        "metadata.ual.stats.jupiterViews.0.place",
        "metadata.ual.stats.jupiterViews.0.value",
        "name",
        "provenance.ual.jupiterId.item",
        "provenance.ual.jupiterId.collection",
        "type",
        "uuid",
    ],
    "bitstream": [
        "item.handle",
        "item.id",
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
        "bitstream.metadata.dc.title.0.value",
        "bitstream.metadata.dc.source.0.value",
        "bitstream.metadata.dc.description.0.value",
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


def flatten_json(json_obj, flattened_schema, prefix=""):
    """
    Flatten JSON object in a very naive way for use in a CSV serialization.
    DSpace Items likely require a more complex flattening to generate "useful" output.
    """
    flat_dict = {}
    for key, value in json_obj.items():
        if isinstance(value, dict):
            flat_dict.update(flatten_json(value, flattened_schema, f"{prefix}{key}."))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if item is not None:
                    flat_dict.update(
                        flatten_json(item, flattened_schema, f"{prefix}{key}.{i}.")
                    )
        else:
            flat_key = f"{prefix}{key}"
            if flat_key in flattened_schema:
                flat_dict[flat_key] = value
            else:
                logging.error("Key not found in schema: %s", flat_key)

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
            provenance_json = convert_string_to_json(provenance["value"])
            dc_provenance_ual_jupiter_id = provenance_json.get(key)
    return dc_provenance_ual_jupiter_id


def convert_string_to_json(string):
    """
    Convert a string to a JSON object
    """
    try:
        return json.loads(string)
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON string: %s", e)
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
