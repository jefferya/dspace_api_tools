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

## Audit steps 

Setup

```bash
    python3 -m venv ./venv/ \
    && \
    ./venv/bin/python3 -m pip install -r src/requirements/requirements.txt
```

The steps to set up a validation run.

1. Use `./jupiter_output_scripts/juptiter_collection_metadata_to_CSV.rb` to export (CSV) Jupiter metadata
2. Use `./dspace_api_export.py` to export (CSV) DSpace metadata

    ```bash
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

3. Use `compare_csv.py` supplying the output from steps 1 & 2 as input, a join and comparison function outputs a CSV file with the validation results. FYI: the join is an outer join which includes null matches in either input file in the output; tweak comparison configuration as required.

    ```bash
    # Set environment variables
    export DSPACE_API_ENDPOINT=https://${SERVER_NAME}/server/api/
    export DSPACE_API_USERNAME=
    export DSPACE_API_PASSWORD=''

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

4. Review the results for PASS/FAIL notices on the validated columns.
 
5. Audit bitstream access restrictions via the web UI

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
