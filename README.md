# DSpace API Tools

A set of tools to interact with the DSpace API in use cases such as aiding migration validation.

## Overview

References for using the DSpace API

* <https://wiki.lyrasis.org/display/DSDOC6x/REST+API#RESTAPI-WhatisDSpaceRESTAPI>
* <https://github.com/DSpace/RestContract/blob/dspace-7_x/README.md#rest-design-principles>
* <https://github.com/DSpace/RestContract/blob/dspace-7_x/endpoints.md>
* <https://github.com/the-library-code/dspace-rest-python>
* <https://wiki.lyrasis.org/display/DSDOC7x/Functional+Overview#FunctionalOverview-DataModel>
* <https://stateless.co/hal_specification.html>

## Requirements

* Python 3.12+ (not tested with versions below 3.12 but may work with 3.10)
* For tests
  * pytest
  * nox

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

## How to Test & Lint :white_check_mark:

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
