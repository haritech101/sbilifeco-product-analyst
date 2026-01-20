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


class FlowTest(IsolatedAsyncioTestCase):
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

        self.url = f"http://localhost:{http_port}/query-ui"

        # Initialise the service(s) here
        self.faker = Faker()

        # Initialise browser
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=False)
        self.page = await self.browser.new_page()

        self.page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) hereself.requests.append(request)
        await self.page.close()
        await self.browser.close()
        await self.pw.stop()
        patch.stopall()

    async def test__submit_valid_query(self) -> None:
        # Arrange
        await self.page.goto(self.url)
        input_query = self.page.locator("#input-query")
        button_submit = self.page.locator("#action-submit")
        panel_history = self.page.locator("#panel-history")
        query = self.faker.sentence()

        # Act
        await input_query.fill(query)
        await button_submit.click()

        await expect(panel_history).to_contain_text(query, timeout=500)
        await expect(panel_history).to_contain_text("Me:", timeout=5000)
