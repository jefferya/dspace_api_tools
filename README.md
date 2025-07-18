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

## Audience / Wayfinding

For those interested in the DSpace API usage, [./src](./src/) directory contains some scripts used as part of the migration audit process. Examples include:

* [dsapce_api_experts.py](#dspace_api_exportspy): bulk exporting content metadata (community, collection, item, and bitstream objects) from DSpace using the API and storing as CSV -- we used to audit but could be used for other purposes.
* Experimental delete item script: [delete_via_api.py](./src/delete_via_api.py)
* Experimental resource policy creator: [dspace_api_resource_policy.py](./src/dspace_api_resource_policy.py)
* Experimental bitsream access control tester: [bistream_access_control_test.py](./src/bitstream_access_control_test.py)

For those interested in our local migration audit process, the [Audit](#audit) section below describes how the local migration audit process evolved locally during the migration from Jupiter(local developed tool) to DSpace/Scholaris. The audit scripts were quickly written during the early DSpace learning phase and were intended for one-time use thus, they lack refinement and, in hindsight, would have benefited from an object-oriented design approach.

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

Note for bitstreams, all DSpace bitstreams are included in the report, including the DSpace generated bitstreams. One can limit and remove if the bundlename is not ORIGINAL.

Item export and audit may contain multiple rows with the same jupiterId in the case where the item is associated with multiple collections. The parent association test may fail.

#### Audit: Technical Details

##### How to how to extend the JSON flattening

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

where the key (e.g., `name`) is the output CSV column label, the columns determine the Jupiter and DSpace fields to compare and the `comparison_function` determines how the comparison is undertaken. These comparison functions are defined earlier in the script. 

### Audit: Setup and Run

Setup for Ruby scripts

Consider cloning this repository into `/tmp` and

* `sudo -u apache bash -c "cd /var/www/sites/jupiter && RAILS_ENV=staging bundle exec rails runner /tmp/dspace_api_tools/jupiter_output_scripts/jupiter_collection_metadata_to_CSV.rb"`
  * change `RAIL_ENV` as needed [development|staging|production]
  * change script as needed

Setup for Python scripts

```bash
    python3 -m venv ./venv/ \
    && \
    ./venv/bin/python3 -m pip install -r src/requirements/requirements.txt
```

The steps to set up a validation run.

1. `./jupiter_output_scripts/juptiter_collection_metadata_to_CSV.rb` to export (CSV) Jupiter metadata (see script for how to run)

2. `./combine_jupiter_item_and_thesis.py` to combine the Jupiter Item and Thesis CSV into a single CSV to ease comparison with Scholaris as Scholaris uses a single data type to store both using optional field to store thesis related metadata.

    ``` bash
    export JUPITER_DIR=~/Downloads/era_export

    # Combine Item and Thesis metadata
    ./venv/bin/python src/combine_jupiter_item_and_thesis.py \
        --input_item ${JUPITER_DIR}/era_export/jupiter_item_2025-03-31_16-26-48.csv \
        --input_thesis ${JUPITER_DIR}/era_export/jupiter_thesis_2025-03-31_16-26-28.csv \
        --output /tmp/jupiter_combined_item_thesis.csv

    # Combine item and Thesis ActiveStorage
    ./venv/bin/python src/combine_jupiter_item_and_thesis.py \
        --input_item ${JUPITER_DIR}/era_export/jupiter_item_activestorage_2025-03-31_16-26-48.csv \
        --input_thesis ${JUPITER_DIR}/era_export/jupiter_thesis_activestroage_2025-03-31_16-26-28.csv \
        --output /tmp/jupiter_combined_activestorage.csv
   ```

3. `./dspace_api_exports.py` to export (CSV) DSpace metadata

    * Option for items and bitstreams: `--random_sample_by_percentage` with default 100% and range between 1-100.
    * Option for items and bitstreams: `--dso_type=item_by_search` and `--dso_type=bitstream_by_search` (fails; see code) which leverage Solr as much as possible to reduce number of API calls (not as well tested)

    ```bash
    # Set environment variables
    export DSPACE_API_ENDPOINT=https://${SERVER_NAME}/server/api/
    export DSPACE_API_USERNAME=
    export DSPACE_API_PASSWORD=''

    export SCHOLARIS_DIR=~/Downloads

    # DSpace export: communities
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output ${SCHOLARIS_DIR}/scholaris_communities.csv \
        --logging_level ERROR \
        --dso_type communities

    # Dspace export: collections
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output ${SCHOLARIS_DIR}/scholaris_collections.csv \
        --logging_level ERROR \
        --dso_type collections

    # DSpace export: items
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output ${SCHOLARIS_DIR}/scholaris_items.csv \
        --logging_level ERROR \
        --dso_type items

    # DSpace export: bitstreams
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output ${SCHOLARIS_DIR}/scholaris_bitstreams.csv \
        --logging_level ERROR \
        --dso_type bitstreams

    ```

4. Use `compare_csv.py` supplying the output from steps 1 & 2 as input, a join and comparison function outputs a CSV file with the validation results. FYI: the join is an outer join which includes null matches in either input file in the output; tweak comparison configuration as required.

    * Note: `--logging_level DEBUG` will log the detailed field values and comparison used in the generated PASS/FAIL summary report
    * Note: `--logging_level ERROR` reduces output

    ```bash

    export JUPITER_DIR=~/Downloads/era_export
    export SCHOLARIS_DIR=~/Downloads

    # Communities audit results
    ./venv/bin/python src/compare_csv.py \
        --input_jupiter ${JUPITER_DIR}/jupiter_community.csv \
        --input_dspace ${SCHOLARIS_DIR}/scholaris_communities.csv \
        --output /tmp/migration_audit_communities_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --logging_level ERROR \
        --type communities

    # Collections audit results
    ./venv/bin/python src/compare_csv.py \
        --input_jupiter ${JUPITER_DIR}/jupiter_collection.csv \
        --input_dspace ${SCHOLARIS_DIR}/scholaris_collections.csv \
        --output /tmp/migration_audit_collections_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --logging_level ERROR \
        --type collections

    # Item audit results
    ./venv/bin/python src/compare_csv.py \
        --input_jupiter ${JUPITER_DIR}/jupiter_combined_item_thesis.csv \
        --input_dspace ${SCHOLARIS_DIR}/scholaris_items.csv \
        --output /tmp/migration_audit_items_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --logging_level DEBUG \
        --type items \
        2> /tmp/z_i

    # Bitstream audit results
    ./venv/bin/python src/compare_csv.py \
        --input_jupiter ${JUPITER_DIR}/jupiter_combined_activestorage.csv \
        --input_dspace ${SCHOLARIS_DIR}/scholaris_bitstreams.csv \
        --output /tmp/migration_audit_bitstreams_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --logging_level DEBUG \
        --type bitstreams \
        2> /tmp/z_b
    ```

5. (optional) In the scenario where some items where intentionally not migrated then filter out the Jupiter/ERA IDs that have not been migrated to reduce the number of failures in the summary reports

    filter a CSV results file by a set of IDs and the column name to filter on in the source CSV file

    ``` bash

    # Filter item audit summary by list of IDs: known IDs in DSpace
    # Assumption: check if an item has failed
    # Adds to output only "input" rows that
    #   have a "jupiter_id" in the "provenance.ual.jupiterId.item"
    #   column of "ids_file"
    ./venv/bin/python src/filter_csv.py \
        --input /tmp/migration_audit_items.csv \
        --column_input jupiter_id \
        --ids_file ${JUPITER_DIR}/id_list_of_migrated_items_2025-05-07.csv \
        --column_ids jupiter_id \
        --output /tmp/migration_audit_items_filtered.csv
 
    # Filter bitstream audit summary by list of IDs: known IDs in DSpace
    # If an item has failed we assume it is not needed
    # Adds to output only "input" rows that
    #   have a "jupiter_id" in the "metadata.ual.jupiterId"
    #   column of "ids_file"
    # Recommend: filter against items or curated list of IDs
    ./venv/bin/python src/filter_csv.py \
        --input /tmp/migration_audit_bitsreams.csv \
        --column_input jupiter_id \
        --ids_file ${SCHOLARIS_DIR}/scholaris_items.csv \
        --column_ids metadata.ual.jupiterId \
        --output /tmp/migration_audit_bitstreams_filtered.csv
    ```

6. Review the results for PASS/FAIL notices on the validated columns.

7. Audit bitstream access restrictions via the web UI

    * Optional:to reduce runtime, split the input list of IDs into multiple files and run multiple instance of the script

    ``` bash

    export DSPACE_ROOT_URL=
    export BITSTREAM_ACCESS_CONTROL_TEST_ROOT=/tmp/z3/z

    ./venv/bin/python3 src/split_csv.py \
        --input ${DSPACE_DIR}/scholaris_items.csv \
        --output ${BITSTREAM_ACCESS_CONTROL_TEST_ROOT}/split/ \
        --output_file_size 100

    # To reduce runtime: remove some source files from ${BITSTREAM_ACCESS_CONTROL_TEST_OUTPUT_ROOT}
   
    for file in ${BITSTREAM_ACCESS_CONTROL_TEST_ROOT}/split/*; do
        base_name=$(basename "$file" .csv) 
        ./venv/bin/python src/bitstream_access_control_test.py \
                --input ${file} \
                --output "${BITSTREAM_ACCESS_CONTROL_TEST_ROOT}/reports/${base_name}_result.csv" \
                --id_field uuid  \
                --root_url ${DSPACE_ROOT_URL}  \
                --logging_level ERROR \
                &
    done

    ```

    * To run sequentially:

    ``` bash
    export DSPACE_ROOT_URL=

    ./venv/bin/python src/bitstream_access_control_test.py \
        --input ${SCHOLARIS_DIR}/scholaris_items.csv \
        --output /tmp/z \
        --id_field uuid  \
        --root_url ${DSPACE_ROOT_URL}  \
        --logging_level INFO
    ```

    * Inspect the following
      * access_restriction column: if blank, no access restriction
      * bitstream_url: if contains "request-a-copy" in the URL then there is an access restriction
      * note: if not empty then there was a failure to load the page or the URL contains no bitstreams
        * TimeoutException can mean that a login prompt was detected or that the site couldn't load

8. Optional: Collection item counts

    ``` bash
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output /tmp/z.csv \
        --dso_type collection_stats
    ```

### Audit: ETDs

Given that ETDs (Theses, etc.) will be migrated at a later date, adjustments to the audit export script have been implemented to allow partial exports. The process will be similar to the above but:

* only a subset of DSpace will be exported
* extract the ETDs from the Jupiter export
* use the above to source files for the audit with the rest of the audit process proceeding as before

The optional ways to export a subset of Item or Bitstream metadata

* Item export given a collection ID

    ``` bash
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output /tmp/z_i.csv \
        --logging_level DEBUG \
        --dso_type items_by_collection_id  \
        --collection_id ba6b42e5-d44d-4e82-b5d3-b66dff1b461c
    ```

* Item export given a file with a list of IDs, one per line with no header

    ``` bash
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output /tmp/z_i.csv \
        --logging_level DEBUG \
        --dso_type items_by_list  \
        --by_list_filename /tmp/zz.csv

    ```

* Bitstream export given a collection ID

    ``` bash
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output /tmp/z_b.csv \
        --logging_level ERROR \
        --dso_type bitstreams_by_collection_id \
        --collection_id ba6b42e5-d44d-4e82-b5d3-b66dff1b461c
    ```

* Bitstream export given a file with a list of IDs, one per line with no header 

    ``` bash
    ./venv/bin/python3 src/dspace_api_exports.py \
        --output /tmp/z_b.csv \
        --logging_level DEBUG \
        --dso_type bitstreams_by_list \
        --by_list_filename /tmp/zz.csv



    ```

As of May 29th, ETDs from Jupiter member_of_path `db9a4e71-f809-4385-a274-048f28eb6814/f42f3da6-00c3-4581-b785-63725c33c7ce` in Scholaris occur in two collections:

* `f3d69d6d-203b-4472-a862-535e749ab216` (permanent, partial ingestion circa May 12th)
* `ba6b42e5-d44d-4e82-b5d3-b66dff1b461c` (temporary holding area ingested May 29th)

To build a Jupiter subset comprised of members of  `db9a4e71-f809-4385-a274-048f28eb6814/f42f3da6-00c3-4581-b785-63725c33c7ce` that have not already been ingested into Scholaris `f3d69d6d-203b-4472-a862-535e749ab216` -- the subset is what we expect to be in `ba6b42e5-d44d-4e82-b5d3-b66dff1b461c`

``` bashi

export JUPITER_FILTER_ROOT=~/Downloads/delete_me_2025-05-15/prd-scholaris/jupiter/

# filter Jupiter 
./venv/bin/python src/filter_csv.py \
    --ids ${JUPITER_FILTER_ROOT}/jupiter_ids_expected_to_be_in_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --column_ids id \
    --input ${JUPITER_FILTER_ROOT}/jupiter_combined_item_thesis.csv  \
    --column_input id \
    --output ${JUPITER_FILTER_ROOT}/jupiter_combined_item_thesis_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv

# filter Jupiter bitstreams
./venv/bin/python src/filter_csv.py \
    --ids ${JUPITER_FILTER_ROOT}/jupiter_ids_expected_to_be_in_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --column_ids id \
    --input ${JUPITER_FILTER_ROOT}/jupiter_combined_activestorage.csv  \
    --column_input item.id \
    --output ${JUPITER_FILTER_ROOT}/jupiter_combined_activestorage_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv

export SCHOLARIS_FILTER_ROOT=~/Downloads/delete_me_2025-05-15/prd-scholaris/scholaris/

# filter Scholaris items
./venv/bin/python src/filter_csv.py \
    --ids ${JUPITER_FILTER_ROOT}/jupiter_ids_expected_to_be_in_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --column_ids id \
    --input ${SCHOLARIS_FILTER_ROOT}/z_i_items_by_collection_id_wihtout_id_maybe_all.csv  \
    --column_input metadata.ual.jupiterId \
    --output ${SCHOLARIS_FILTER_ROOT}/scholaris_item_thesis_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv


# filter Scholaris bitstreams 
./venv/bin/python src/filter_csv.py \
    --ids ${JUPITER_FILTER_ROOT}/jupiter_ids_expected_to_be_in_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --column_ids id \
    --input ${SCHOLARIS_FILTER_ROOT}/scholaris_bitstreams_ingested_into_scholaris_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c_may_29th.csv \
    --column_input provenance.ual.jupiterId.item \
    --output ${SCHOLARIS_FILTER_ROOT}/scholaris_bitstream_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv


# Item audit results
./venv/bin/python src/compare_csv.py \
    --input_jupiter ${JUPITER_DIR}/jupiter_combined_item_thesis_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --input_dspace ${SCHOLARIS_DIR}/scholaris_item_thesis_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --output /tmp/migration_audit_items_$(date +%Y-%m-%d_%H:%M:%S).csv \
    --logging_level DEBUG \
    --type items \
    2> /tmp/z_i.log

# Bitstream audit results
./venv/bin/python src/compare_csv.py \
    --input_jupiter ${JUPITER_DIR}/jupiter_combined_activestorage_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --input_dspace ${SCHOLARIS_DIR}/scholaris_bitstream_subset_theses_and_dissertations_ba6b42e5-d44d-4e82-b5d3-b66dff1b461c.csv \
    --output /tmp/migration_audit_bitstreams_$(date +%Y-%m-%d_%H:%M:%S).csv \
    --logging_level DEBUG \
    --type bitstreams \
    2> /tmp/z_b.log


```

## dspace_api_exports.py

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
./venv/bin/python3 src/dspace_api_exports.py \
    --output /tmp/z.log \
    --logging_level ERROR \
    --dso_type communities
```

Where `--dso_type` is `[communities|collections|items|items_by_search|items_by_list|items_by_collection_id|people|bitstreams|bitstreams_by_list|bitstreams_by_collection_id]`

## Jupiter Delta Report

### Jupiter Delta Report: Overview

Given that not all ERA content can be frozen, a delta report aims to communicate any changes to the ERA content from a specified date until the time the report is run. The report aims to communicate each content change leveraging the same data enabling ERA/Jupiter versions UI. Each change event is recorded as a row in a Google Sheet contain both the changed Jupiter fieldname/value data and the Scholaris mappings for the fieldname/value data.

The assumption is the number of actionable changes is small and a human can leverage the information in the report to

* see that a Jupiter object has changed
* identify the Scholaris fieldnames to update and the Scholaris value

### Delta Report: How to use

The report can be presented and shared as a Google Doc to allow users to sort, search, modify as needed.

An early example <https://docs.google.com/spreadsheets/d/1GWxwEtM0EOyoPP5RUrf1oQCtIVz1re-8n0Be4Kybt8E/edit?gid=0#gid=0>

The header includes:

```csv
type,change_id,jupiter_id,is_jupiter_currently_readonly,changed at,event,jupiter delta,scholaris mapped delta,jupiter delta formatted,scholaris mapped delta formatted 
```

Where:

* type: item|thesis
* change_id: change event id (PaperTrail::Version ID)
* jupiter_id: ERA ID
* is_jupiter_currently_readonly: "true" if the ERA object is currently read only
* read_only_event: "true" if this change event only updated the read only field and the obj updated at timestamp
* changed_at: change event timestamp
* event: the type of the change record: update|destroy
* jupiter delta: jupiter change event details (what field plus old => new values)
* jupiter delta formatted: an easier to read version
* scholaris mapper: the jupiter delta mapped to Scholaris fieldname and new value equivalents
* scholaris mapper formatted: an easier to read version

Process thoughts:

* In ERA, changing an object to "read only" creates a new version change event: the read_only_event column that indicated if change event only updates read only status thus allow one to filter/order these events if too numerous
* Sort by item_id & date ascending: this allows grouping a sequence of updates over time; if the same field changed multiple times then use the most recent.
* Event "destroy" means the object has been deleted and there will be no Scholaris mapping
  * Event "destroy" will create a long change record -- "top align" text in cells to see the text

### Status

* 2025-04-14:
  * Prototype of Jupiter Items
  * In-progress: Jupiter community, collection, thesis, and bitstreams

### Delta Report: How to generate

For Item/Thesis/Collection/Community, see script for details: `jupiter_output_scripts/jupiter_delta.rb`

* `sudo -u apache bash -c "cd /var/www/sites/jupiter && RAILS_ENV=staging bundle exec rails runner /tmp/dspace_api_tools/jupiter_output_scripts/jupiter_delta.rb"`
  * change `RAIL_ENV` as needed [development|staging|production]

 Rough outline:

* Set date in script and run `jupiter_output_scripts/jupiter_delta.rb`
* Upload CSV into Google Docs for Sharing

For the Bitstrams, see script for details: `jupiter_output_scripts/jupiter_delta_bitstreams.rb`

Rough outline:

* Find ActivieStorage bitstreams created after given date
* The list should be the same as `jupiter_delta.rb` as changing the metadata updates ActiveStorage created_at timestamps and there does not appear to be a way to update a bitstream (only create a new and delete the old).
* Upload CSV into Google Docs for Sharing

## Jupiter Statistics to Scholaris

Rough outline

* Generate CSV report of Jupiter statistics, see `jupiter_output_scripts/jupiter_statistics_metadata_to_CSV`
* Generate CSV report from DSpace, `dspace_api_exports.py`
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
