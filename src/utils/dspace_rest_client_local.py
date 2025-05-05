# pylint: disable=E0213,R0913,R0917,E1124,E1102

"""
Extends the DSpaceClient to provide a local implementation of the DSpace REST API client.
Fixes the problem where the decorator and generator search_objects_iter doesn't include the
"embed" parameter as it assumes the "next" link contains all the params needed for the correct next page.
Also, there are multiple linting errors is the dsapce_rest_client that are disabled here
    * pylint: disable=E0213,R0913,R0917,E1124,E1102
Tested: DSpace 7
"""

import functools

from urllib.parse import urlparse, parse_qs

from dspace_rest_client.client import DSpaceClient
from dspace_rest_client.client import parse_params
from dspace_rest_client.models import SimpleDSpaceObject


class DSpaceClientLocal(DSpaceClient):
    """
    Extends the DSpaceClient to provide a local implementation of the DSpace REST API client.
    """

    # Base class should set this as an instance variable in the constructor
    ITER_PAGE_SIZE = 100

    def paginated_local(embed_name, item_constructor, embedding=lambda x: x):
        """
        @param embed_name: The key under '_embedded' in the JSON response that contains the
        resources to be paginated. (e.g. 'collections', 'objects', 'items', etc.)
        @param item_constructor: A callable that takes a resource dictionary and returns an item.
        @param embedding: Optional post-fetch processing lambda (default: identity function)
        for each resource
        @return: A decorator that, when applied to a method, follows pagination and yields
        each resource
        """

        def decorator(fun):
            @functools.wraps(fun)
            def decorated(self, *args, **kwargs):
                def do_paginate(url, params):
                    params["size"] = self.ITER_PAGE_SIZE

                    while url is not None:
                        r_json = embedding(self.fetch_resource(url, params))
                        for resource in r_json.get("_embedded", {}).get(embed_name, []):
                            yield item_constructor(resource)

                        if "next" in r_json.get("_links", {}):
                            url = r_json["_links"]["next"]["href"]
                            # assume the ‘next’ link contains all the
                            # params needed for the correct next page:
                            # params = {}
                            # 2025-05-05
                            # Local instance this assumption is wrong
                            #   because DSpace 7 does not include the "embed" param
                            # Add back any missing params
                            parsed_url = urlparse(url)
                            url_params = parse_qs(parsed_url.query)
                            params = {
                                key: value
                                for key, value in params.items()
                                if key not in url_params
                            }
                        else:
                            url = None

                return fun(do_paginate, self, *args, **kwargs)

            return decorated

        return decorator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @paginated_local(
        embed_name="objects",
        item_constructor=lambda x: SimpleDSpaceObject(
            x["_embedded"]["indexableObject"]
        ),
        embedding=lambda x: x["_embedded"]["searchResult"],
    )
    def search_objects_iter(
        do_paginate,
        self,
        query=None,
        scope=None,
        filters=None,
        dso_type=None,
        sort=None,
        configuration="default",
        embeds=None,
    ):
        """
        Do a basic search as in search_objects, automatically handling pagination by requesting
        the next page when all items from one page have been consumed
        @param query:   query string
        @param scope:   uuid to limit search scope, eg. owning collection, parent community, etc.
        @param filters: discovery filters as dict eg. {'f.entityType': 'Publication,equals', ... }
        @param sort: sort eg. 'title,asc'
        @param dso_type: DSO type to further filter results
        @param configuration: Search (discovery) configuration to apply to the query
        @param embeds:  Optional list of embeds to apply to each search object result
        @return:        Iterator of SimpleDSpaceObject
        """

        if filters is None:
            filters = {}
        url = f"{self.API_ENDPOINT}/discover/search/objects"
        params = parse_params(embeds=embeds)
        if query is not None:
            params["query"] = query
        if scope is not None:
            params["scope"] = scope
        if dso_type is not None:
            params["dsoType"] = dso_type
        if sort is not None:
            params["sort"] = sort
        if configuration is not None:
            params["configuration"] = configuration

        return do_paginate(url, {**params, **filters})
