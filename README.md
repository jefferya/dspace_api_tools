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

## Validation

Setup

```bash
    python3 -m venv ./venv/ \
    && \
    ./venv/bin/python3 -m pip install -r src/requirements/requirements.txt
```

The steps to set up a validation run.

1. Use `./jupiter_output_scripts/juptiter_collection_metadata_to_CSV.rb` to export (CSV) Jupiter metadata
2. Use `./dspace_api_experiment.py` to export (CSV) DSpace metadata
3. Use `compare_csv.py` supplying the output from steps 1 & 2 to output a CSV file with the validation results (tweak comparison configuration as required).

    ```bash

    # Communities validation results
    venv/bin/python src/compare_csv.py \
        --input_jupiter ~/Downloads/era_export/jupiter_community_2025-03-06_12-05-19.csv \
        --input_dspace ~/Downloads/scholaris_communities.csv \
        --output /tmp/communities_validation_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --type communities

    # Collections validation results
    venv/bin/python src/compare_csv.py \
        --input_jupiter ~/Downloads/era_export/jupiter_collection_2025-03-06_12-08-01.csv \
        --input_dspace ~/Downloads/scholaris_collections.csv \
        --output /tmp/collections_validation_$(date +%Y-%m-%d_%H:%M:%S).csv \
        --type collections
    ```

4. Review the results for PASS/FAIL notices on the validated columns.

## dspace_api_experiment.py

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
./venv/bin/python3 src/dspace_api_experiment.py \
    --output /tmp/z.log \
    --logging_level ERROR \
    --dso_type communities
```

Where `--dso_type` is `[communities|collections|items|people]`

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
