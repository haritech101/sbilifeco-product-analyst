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
from asyncio import sleep
from playwright.async_api import async_playwright, Playwright, Route, Request, expect
from sbilifeco.boundaries.id_name_repo import IDNameEntity


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".env")

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.base_url = f"http://localhost:{http_port}/ingest-ui/"

        # Initialise the service(s) here
        self.faker = Faker()
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        self.ingest_url_requests: list[Request] = []

        self.page.on("console", lambda msg: print(f"PAGE LOG: {msg}"))

        self.materials = [
            IDNameEntity(
                id=uuid4().hex,
                name=",".join(self.faker.words(3)),
                created_at=self.faker.date_time_this_year(),
            )
            for i in range(1, 6)
        ]

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        self.ingest_url_requests.clear()
        await self.page.close()
        await self.browser.close()
        await self.playwright.stop()
        patch.stopall()

    async def gather_request(self, req: Request):
        if (
            "/api/v1/ingest-requests" in req.url
            or "/api/v1/material-list-requests" in req.url
        ):
            self.ingest_url_requests.append(req)

    async def route_request_ingestion(self, route: Route) -> None:
        if route.request.url.endswith("/ingest-requests"):
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=Response.ok(uuid4().hex).model_dump_json(),
            )
        elif "/ingest-requests" in route.request.url:
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=Response.ok(None).model_dump_json(),
            )
        else:
            await route.continue_()

    async def route_request_materials(self, route: Route) -> None:
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=Response.ok(self.materials).model_dump_json(),
        )

    async def test_page_loads(self) -> None:
        # Arrange
        await self.page.route(
            "**/api/v1/material-list-requests", self.route_request_materials
        )

        # Act
        await self.page.goto(self.base_url)

        # Assert
        await self.page.wait_for_url(self.base_url)

        await expect(self.page.locator("#panel-materials div.row")).to_have_count(
            len(self.materials)
        )

    async def test_error_when_blank_content_name(self) -> None:
        # Arrange
        await self.page.route(
            "**/api/v1/material-list-requests", self.route_request_materials
        )
        await self.page.goto(self.base_url)
        upload_button = await self.page.wait_for_selector(
            "#action-upload", timeout=5000
        )
        assert upload_button is not None
        feedback_banner = await self.page.query_selector("#banner-feedback-upload")
        assert feedback_banner is not None

        # Act
        await upload_button.click()

        # Assert
        self.assertTrue(
            await feedback_banner.inner_text(), "No validation error produced"
        )

    async def test_error_when_no_file_selected(self) -> None:
        # Arrange
        await self.page.route(
            "**/api/v1/material-list-requests", self.route_request_materials
        )
        await self.page.goto(self.base_url)
        content_name_input = await self.page.wait_for_selector(
            "#input-content-name", timeout=5000
        )
        assert content_name_input is not None
        upload_button = await self.page.query_selector("#action-upload")
        assert upload_button is not None
        feedback_banner = await self.page.query_selector("#banner-feedback-upload")
        assert feedback_banner is not None

        # Act
        await content_name_input.fill(self.faker.word())
        await upload_button.click()

        # Assert
        self.assertTrue(
            await feedback_banner.inner_text(), "No validation error produced"
        )

    async def test_proceed_when_valid_input(self) -> None:
        # Arrange
        await self.page.route(
            "**/api/v1/ingest-requests**", self.route_request_ingestion
        )
        await self.page.route(
            "**/api/v1/material-list-requests", self.route_request_materials
        )
        self.page.on("request", self.gather_request)

        await self.page.goto(self.base_url)
        content_name_input = await self.page.wait_for_selector(
            "#input-content-name", timeout=5000
        )
        assert content_name_input is not None
        file_input = await self.page.query_selector("#input-content-file")
        assert file_input is not None
        upload_button = await self.page.query_selector("#action-upload")
        assert upload_button is not None
        feedback_banner = await self.page.query_selector("#banner-feedback-upload")
        assert feedback_banner is not None

        content_title = " ".join(self.faker.words(3))
        self.materials.append(
            IDNameEntity(
                id=uuid4().hex,
                name=content_title,
                created_at=datetime.now(),
            )
        )

        # Act
        await content_name_input.fill(content_title)
        await file_input.set_input_files("test/fixtures/brochure.pdf")
        await upload_button.click()

        # Assert
        await sleep(1)

        self.assertEqual(len(self.ingest_url_requests), 4)
        self.assertTrue(
            self.ingest_url_requests[0].url.endswith("/api/v1/material-list-requests"),
            "Third request should fetch updated material list",
        )
        self.assertTrue(
            self.ingest_url_requests[1].url.endswith("/api/v1/ingest-requests"),
            "First request should request ingestion",
        )
        self.assertTrue(
            "/api/v1/ingest-requests" in self.ingest_url_requests[2].url,
            "Second request should inject data into current ingestion request",
        )
        self.assertTrue(
            self.ingest_url_requests[3].url.endswith("/api/v1/material-list-requests"),
            "Third request should fetch updated material list",
        )

        self.assertIn("success", (await feedback_banner.inner_text()).lower())

        self.assertEqual(await content_name_input.input_value(), "")
        self.assertEqual(await file_input.input_value(), "")

        uploaded_content_name = self.page.get_by_text(content_title)
        await expect(uploaded_content_name).to_be_visible()
