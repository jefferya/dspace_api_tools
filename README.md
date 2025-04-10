# DSpace API Tools

A set of tools to interact with the DSpace API in use cases such as aiding migration validation.

## Overview

References for using the DSpace API

* REST API intro: <https://wiki.lyrasis.org/display/DSDOC6x/REST+API#RESTAPI-WhatisDSpaceRESTAPI>
* REST API design: <https://github.com/DSpace/RestContract/blob/dspace-7_x/README.md#rest-design-principles>
* REST API endpoints: <https://github.com/DSpace/RestContract/blob/dspace-7_x/endpoints.md>
* Data Model: <https://wiki.lyrasis.org/display/DSDOC7x/Functional+Overview#FunctionalOverview-DataModel>
* Acronym and definitions: <https://docs.google.com/document/d/11meAwAI-RPipoYs9uuJYTvvi5mkiFQp7HPAnERD03rA/edit?tab=t.0>
* HAL spec: <https://stateless.co/hal_specification.html>
* HAL Browser Demo: <https://demo.dspace.org/server/#/server/api>
* Python client: <https://github.com/the-library-code/dspace-rest-python>

## Requirements

* Python 3.12+ (not tested with versions below 3.12 but may work with 3.10)
* For tests
  * pytest
  * nox

## Audit

One piece of the migration from Jupiter to Scholaris, in particular the validation stage, is a content audit stage. The overview section describes the audit with a following section describing the technical steps to run the audit workflow.

### Audit: Overview

The audit workflow starts with CSV exports of content (i.e., communities, collections, items, thesis, and bitstreams) from both Jupiter and a DSpace instance. An audit or comparison script runs a set of tests and builds a report for human review with potential audit error flagged for further human investigation.

What is content is audited:

* Community
  * existence
  * fields (labels from DSpace API): name, description, abstract, title

* Collection
  * existence
  * associated to the correct community (by name as DSpace doesn't store legacy community jupiter id)
  * fields (labels from DSpace API): name, description, abstract, title

* Bitstream 
  * existence
  * associated with the correct Item (ID & Name)
  * correct sequence number
  * fields (labels from DSpace API): file_name, checksum

* Item
  * existence
  * associated with the correct collection
  * fields: name, description, title, contributor, creator, type, language, subject, date.issued, rights/license, abstract, access_rights, dissertant, supervisor, committee members, degree grantor, degree level, date.graduation, department

A second audit process includes auditing the web UI to determine the access rights of the bitstreams.

### Audit: details

1. Export Jupiter metadata as CSV via [./jupiter_output_scripts/jupiter_collection_metadata_to_CSV](./jupiter_output_scripts/jupiter_collection_metadata_to_CSV)
    * Export Community, Collection, Item, Thesis, and Bitstream metadata as CSV. Includes special handling for the following types to allow auditing of associations (e.g., collection associated with correct community) :
        * Collection: include the Community label as Scholaris doesn't retain Community Jupiter provenance
        * Bitstreams: include Item association information

2. Combine Item and Thesis into a common CSV [./src/combine_juptiter_item_and_thesis.py](./src/combine_jupiter_item_and_thesis.py)
    * DSpace combines item and thesis into a single data type "Item" thus to ease comparison, item and thesis CSV from Jupiter are combined into a single CSV

3. Export DSpace metadata as CSV from the DSpace REST API [./src/dspace_api_exports.py](./src/dspace_api_exports.py).
    * Export Community, collection, Item, and Bitstreams and flattens the JSON output into a CSV

4. Content audit  [./src/compare_csv.py](./src/compare_csv.py)
    * Audit based on a configurable set of named verification steps specific to each type (i.e., Community, Collection, Item, Bitstream) and produce a CSV output summerizing the results. Adding additional steps is highly configurable and may take as little as 10min to add.

5. Bitstream URL audit [./src/bitstream_access_control_test.py](./src/bitstream_access_control_test.py)
    * Audit a list of URL's as an unauthenicated/anonymous user to determine if the Bitstreams are
      * reachable
      * metadata reachable but bitstreams restricted
      * metadata and bitstreams restricted
      * or the url is not found

6. Human review of the output of the last two steps
    * Content audit:
      * Review the audit summary for "FAIL" messages
      * Used the following to help diagnose: the Google Sheet contains tabs for the audit output plus the Jupiter and DSpace CSV export used in the audit along with the logging output of the script

#### How to use the audit output

The content audit report will generate a CSV file summarizing the results. If the script is run with `DEBUG` logging level one can gain more insight into the results, if necessary.

The resulting CSV contain three types of columns:

* first column is the index (empty if no ERA object)
* contextual columns: label, jupiter_updated_at,dspace_lastModified,jupiter_id,dspace_id
* audit pass/fail column with a header label matching a config entry in `compare_csv.py`

For example, the bitstream audit header:

``` csv
index (empty if no ERA obj),label,jupiter_updated_at,dspace_lastModified,jupiter_id,dspace_id,name,checksum,sequence,parent_item_id,parent_item_name
```

``` csv
"('fc83bb92-bbc6-4cce-9a81-b55f00ad3285', 1)",The Whisper of the Scarlet Buffalo,2018-09-25 23:53:16 UTC,,fc83bb92-bbc6-4cce-9a81-b55f00ad3285,5defda8a-05d7-44db-a650-df028a5dd525,PASS,PASS,PASS,PASS,PASS
```

I'll import into a Google Sheet to leverage the power of the grid layout

`index` is empty if a thing is not found in Jupiter (e.g., a UI entered, hand-crafted test in Scholaris)
`dspace_id` is nan/empty if a thing is not found in DSpace (e.g., an ERA item has not been migrated into Scholaris)


#### Audit: how to enhance

##### JSON flattening

DSpace API produces JSON. The JSON is flattened into CSV (`flatten_json` method). The `utilities.py` contains a set of methods to flatten the JSON in different ways depending on the key. For example, we only want the "value":

``` python
        "dc.contributor.author" : [ {
        "value" : "Item - Test Creator 1",
        "language" : null,
        "authority" : null,
        "confidence" : -1,
        "place" : 0
        }
```

There is list in `utilities.py` that contains the JSON keys to export (`CSV_FLATTENED_HEADERS`) and the JSON keys to deconstruct (`fields_deconstruct_to_list_of_values`) in the above example. If a "key not found" error occurs, then the key needs to be added to `CSV_FLATTENED_HEADERS` and possibily `fields_deconstruct_to_list_of_values`. Also, perhaps a `src/tests/asset` file if a new test is added.

##### How to add new audit cases via config

The content audit is configured and run via `src/compare_csv.py`. For each DSpace data model type, there is a configuration named `${type}_columns_to_compoare` (e.g., bitstreams_columns_to_compoare). Each comparison looks like:

``` python
"comparison_types": {
        "name": {
            "columns": {"jupiter": "filename", "dspace": "bitstream.name"},
            "comparison_function": string_compare,
        },
        "checksum": {
            "columns": {
                "jupiter": "checksum",
                "dspace": "bitstream.checksum.value",
            },
            "comparison_function": activestorage_to_dspace_checksum_compare,
        },
        ...
```

where the key (e.g., `name`) is the output CSV column label, the columns determine the Jupiter and DSpace fields to compare and the `comparison_function` determines how the comparison is undertaken. These comparision functions are defined earlier in the script. 

### Audit: Setup and Run

```bash
    python3 -m venv ./venv/ \
    && \
    ./venv/bin/python3 -m pip install -r src/requirements/requirements.txt
```

The steps to set up a validation run.

1. Use `./jupiter_output_scripts/juptiter_collection_metadata_to_CSV.rb` to export (CSV) Jupiter metadata
2. Use `./combine_jupiter_item_and_thesis.py` to combine the Jupiter Item and Thesis CSV into a singel CSV to ease comparisioin with Scholaris as Scholaris uses a single type to store both using optional field to store thesis related metadata.
3. Use `./dspace_api_export.py` to export (CSV) DSpace metadata

    ```bash
    # Set environment variables
    export DSPACE_API_ENDPOINT=https://${SERVER_NAME}/server/api/
    export DSPACE_API_USERNAME=
    export DSPACE_API_PASSWORD=''

    # DSpace export: communities
    ./venv/bin/python3 src/dspace_api_export.py \
        --output ~/Downloads/scholaris_communities.csv \
        --logging_level ERROR \
        --dso_type communities

    # Dspace export: collections 
    ./venv/bin/python3 src/dspace_api_export.py \
        --output ~/Downloads/scholaris_collections.csv \
        --logging_level ERROR \
        --dso_type collections 

    # DSpace export: items 
    ./venv/bin/python3 src/dspace_api_export.py \
        --output ~/Downloads/scholaris_items.csv \
        --logging_level ERROR \
        --dso_type items 
        
    # DSpace export: bibstreams 
    ./venv/bin/python3 src/dspace_api_export.py \
        --output ~/Downloads/scholaris_bitstreams.csv \
        --logging_level ERROR \
        --dso_type bitstreams 
        
    ```

4. Use `compare_csv.py` supplying the output from steps 1 & 2 as input, a join and comparison function outputs a CSV file with the validation results. FYI: the join is an outer join which includes null matches in either input file in the output; tweak comparison configuration as required.

    ```bash

    # Communities audit results
    venv/bin/python src/compare_csv.py \
        --input_jupiter ~/Downloads/era_export/jupiter_community_2025-03-06_12-05-19.csv \
        --input_dspace ~/Downloads/scholaris_communities.csv \
        --output /tmp/migration_audit_communities_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --type communities

    # Collections audit results
    venv/bin/python src/compare_csv.py \
        --input_jupiter ~/Downloads/era_export/jupiter_collection_2025-03-06_12-08-01.csv \
        --input_dspace ~/Downloads/scholaris_collections.csv \
        --output /tmp/migration_audit_collections_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --type collections
    
    # Item audit results
    venv/bin/python src/compare_csv.py \
        --input_jupiter ~/Downloads/era_export/jupiter_items_2025-03-06_12-08-01.csv \
        --input_dspace ~/Downloads/scholaris_items.csv \
        --output /tmp/migration_audit_bitstreams_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --type bitstreams 
    
    # Bitstream audit results
    venv/bin/python src/compare_csv.py \
        --input_jupiter ~/Downloads/era_export/jupiter_items_2025-03-06_12-08-01.csv \
        --input_dspace ~/Downloads/scholaris_bitstreams.csv \
        --output /tmp/migration_audit_bitstreams_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --type bitstreams 
    ```

5. Review the results for PASS/FAIL notices on the validated columns.

6. Audit bitstream access restrictions via the web UI

    ``` bash
    ./venv/bin/python src/bitstream_access_control_test.py \
        --input /tmp/x
        --output /tmp/z
        --id_field uuid 
        --root_url ${DSPACE_ROOT_URL} 
        --logging_level INFO
    ```

    * Inspect the following
      * access_restriction column: if blank, no access restriction
      * bitstream_url: if contains "request-a-copy" in the URL then there is an access restriction
      * note: if not empty then there was a failure to load the page or the URL contains no bitstreams
        * TimeoutException can mean that a login prompt was detected or that the site couldn't load

## dspace_api_export.py

Test exporting content from the DSpace API using <https://pypi.org/project/dspace-rest-client>.

Setup

```bash
    python3 -m venv ./venv/ \
    && \
    ./venv/bin/python3 -m pip install -r src/requirements/requirements.txt
```

Set the following environment variables, the username/password are the same as your web UI login (though this might change once SSO is enabled)

```bash
export DSPACE_API_ENDPOINT=https://${SERVER_NAME}/server/api/
export DSPACE_API_USERNAME=
export DSPACE_API_PASSWORD=''
```

Run Python from the virtual environment (see Python Virtual Environment documentation for details). One method:

```bash
./venv/bin/python3 src/dspace_api_export.py \
    --output /tmp/z.log \
    --logging_level ERROR \
    --dso_type communities
```

Where `--dso_type` is `[communities|collections|items|people|bitstreams]`


## Jupiter Delta

`jupiter_output_scripts/jupiter_delta.rb`

## Jupiter Statistics to Scholaris

Rough outline

* Generate CSV report of Jupiter statistics, see `jupiter_output_scripts/jupiter_statistics_metadata_to_CSV`
* Generate CSV report from DSpace, `dsapce_api_exports.py`
* The quick approach: 
  * place both CSV reports into separate tabs in a Google Sheet
  * use XLOOKUP to align based on jupiter ID
  * add column to that compares the "view"|"download" counts between the two reports (`IF` to add a sortable value in the new column)
    * optional: change colour if different
  * add column with Scholaris URL for usability

## How to Test & Lint

To have the code ready for production, simply run:

```bash
    nox
```

To test, run:

```bash
    nox -s test
```

To lint, run:

```bash
    nox -s lint
```

## Test content

Test file permissions 2025-03-19:

* <http://198.168.187.81:4000/collections/c3c2d7e6-4efa-43f5-8345-0b6aa16d2af9>
* <https://ualberta-dev.scholaris.ca/collections/f2190650-69ee-4989-a5f9-399251c3314b>
