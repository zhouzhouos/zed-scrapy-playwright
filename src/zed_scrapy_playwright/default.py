# from abc import ABC, abstractmethod
# from collections.abc import Sequence
# from datetime import timedelta
# from pathlib import Path
# from typing import TYPE_CHECKING, Literal, Self, TypedDict

# from scrapy import Request
import scrapy.http
from playwright.async_api import Page, async_playwright

# from scrapy.http.response import
from zed_scrapy_playwright import definition as Z
from zed_scrapy_playwright import interface as I


class Provider(I.Provider):
    """moren"""

    async def _start(self):
        self.playwright_context_manager = async_playwright()
        self.playwright = await self.playwright_context_manager.start()
        self.default_browser = await self.playwright.chromium.launch()
        self.default_context = await self.default_browser.new_context()
        return self

    async def start(self):
        if self.config is None:
            return await self._start()

        self.playwright_context_manager = async_playwright()
        self.playwright = await self.playwright_context_manager.start()
        # self.default_browser = await self.playwright.chromium.launch()
        # self.default_context = await self.default_browser.new_context()

        if self.config["browser_type"] == "chrome":
            self.default_browser = await self.playwright.chromium.launch(
                **self.config["chrome_params"]
            )
            self.default_context = await self.default_browser.new_context(
                no_viewport=True
            )
            return self
        else:
            raise NotImplementedError

    async def close(self):
        await self.default_context.close()
        await self.default_browser.close()
        await self.playwright.stop()
        await self.playwright_context_manager.__aexit__()

    async def css(self, selector) -> Page:
        return await self.default_context.new_page()

    async def takeover(self, request: Z.Request):
        page = await self.css(request.selector)
        ret = await request.execution(Z.ExecParam(request, page))

        if ret is None:
            response = scrapy.http.HtmlResponse(
                url=page.url,
                # status=200,
                # headers=None,
                # body=b"",
                # flags=None,
                request=request,
                # certificate=None,
                # ip_address=None,
                # protocol=None,
            )
            response._encoding = "utf-8"
            response._set_body(await page.content())
            return response
        else:
            return Z.Response(ret, request=request)
