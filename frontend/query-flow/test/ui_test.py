import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from re import compile
from asyncio import sleep
from playwright.async_api import async_playwright, expect, Request, Route
from sbilifeco.boundaries.product_analyst.query_flow import RatedAnswer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.api_base_url = getenv(EnvVars.api_base_url, Defaults.api_base_url)
        self.material_queries_path = getenv(
            EnvVars.material_queries_path,
            Defaults.material_queries_path,
        )

        self.url = f"http://localhost:{http_port}/product-query-ui"

        # Initialise the service(s) here
        self.faker = Faker()

        # Initialise browser
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=False)
        self.page = await self.browser.new_page()

        self.page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))

        self.requests: list[Request] = []
        self.page.on("request", self.gather_request)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) hereself.requests.append(request)
        await self.page.close()
        await self.browser.close()
        await self.pw.stop()
        patch.stopall()

    def gather_request(self, request: Request) -> None:
        if request.url.startswith(self.api_base_url):
            self.requests.append(request)

    def handle_request(self, reply: str):
        async def __handle(route: Route, request: Request) -> None:
            print(f"Outbound request to --> {request.url}")
            if request.url.endswith(self.material_queries_path):
                await route.fulfill(
                    status=200, json=Response.ok(uuid4().hex).model_dump()
                )
            elif self.material_queries_path in request.url:
                await route.fulfill(
                    status=200,
                    json=Response.ok(
                        RatedAnswer(answer=reply, sources=[])
                    ).model_dump(),
                )
            else:
                await route.continue_()

        return __handle

    async def test__page_loads(self) -> None:
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("domcontentloaded", timeout=3000)

    async def test__page_has_components(self) -> None:
        await self.page.goto(self.url)

        history_panel = self.page.locator("#panel-history")
        await expect(history_panel).to_be_visible(timeout=500)

        query_input = self.page.locator("#input-query")
        await expect(query_input).to_be_visible(timeout=500)

        submit_button = self.page.locator("#action-submit")
        await expect(submit_button).to_be_visible(timeout=500)

    async def test__error_with_empty_query(self) -> None:
        await self.page.goto(self.url)

        button_submit = self.page.locator("#action-submit")
        await button_submit.click()

        panel_feedback = self.page.locator("#panel-feedback")
        await expect(panel_feedback).to_be_visible(timeout=500)
        await expect(panel_feedback).to_contain_text(
            "Question cannot be empty", timeout=500
        )

    async def test__submit_valid_query(self) -> None:
        # Arrange
        await self.page.goto(self.url)
        input_query = self.page.locator("#input-query")
        button_submit = self.page.locator("#action-submit")
        panel_history = self.page.locator("#panel-history")
        query = self.faker.sentence()
        reply = self.faker.paragraph()

        await self.page.route(
            "**",
            self.handle_request(reply),
        )

        # Act
        await input_query.fill(query)
        await button_submit.click()

        await expect(panel_history).to_contain_text(query, timeout=500)
        await expect(panel_history).to_contain_text(reply, timeout=500)
