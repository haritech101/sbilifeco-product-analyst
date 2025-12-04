from __future__ import annotations
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.product_analyst.query_flow.paths import QueryFlowPaths
from sbilifeco.boundaries.product_analyst.query_flow import BaseQueryFlow, RatedAnswer
from sbilifeco.models.base import Response
from fastapi import Request as FastRequest


class QueryFlowHttpServer(HttpServer):
    def __init__(self) -> None:
        super().__init__()
        self.query_flow: BaseQueryFlow

    def set_query_flow(self, query_flow: BaseQueryFlow) -> QueryFlowHttpServer:
        self.query_flow = query_flow
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(QueryFlowPaths.BASE)
        async def request_search() -> Response[str]:
            try:
                # Validate request
                ...

                # Request gateway
                res = await self.query_flow.request_search()

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)

        @self.post(QueryFlowPaths.SINGLE_QUERY)
        async def search(id: str, req: FastRequest) -> Response[RatedAnswer]:
            try:
                # Validate request
                ...

                # Triage request
                query = (await req.body()).decode()

                # Request gateway
                res = await self.query_flow.search(id, query)

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)
