from typing import cast
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.cp.product_analyst.query_flow.paths import QueryFlowPaths
from sbilifeco.boundaries.product_analyst.query_flow import (
    BaseQueryFlow,
    RatedAnswer,
    RatedSource,
)
from sbilifeco.models.base import Response


class QueryFlowHttpClient(HttpClient, BaseQueryFlow):
    def __init__(self):
        BaseQueryFlow.__init__(self)
        HttpClient.__init__(self)
        self.proto = "http"
        self.host = "localhost"
        self.port = 80

    async def request_search(self) -> Response[str]:
        try:
            # Set up request
            url = f"{self.url_base}{QueryFlowPaths.BASE}"
            req = Request(
                url=url,
                method="POST",
            )

            # Call
            res = await self.request_as_model(req)

            # Triage response
            ...

            # Return response
            return res
        except Exception as e:
            return Response.error(e)

    async def search(
        self, search_request_id: str, query: str, num_results: int = 5
    ) -> Response[RatedAnswer]:
        try:
            # Form request
            url = f"{self.url_base}{QueryFlowPaths.SINGLE_QUERY.format(id=search_request_id)}"
            req = Request(
                url=url,
                method="POST",
                headers={"Content-Type": "text/plain"},
                data=query,
            )

            # Call
            res = cast(Response[RatedAnswer], await self.request_as_model(req))

            # Triage response
            if res.payload:
                res.payload = RatedAnswer.model_validate(res.payload)
                res.payload.sources = [
                    RatedSource.model_validate(map) for map in res.payload.sources
                ]

            # return response
            return res
        except Exception as e:
            return Response.error(e)
