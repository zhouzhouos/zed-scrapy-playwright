# from scrapy.http import Response, TextResponse
from collections.abc import Awaitable, Callable
from typing import Any, Literal, Self

import scrapy
import scrapy.http
from playwright.async_api import Page
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured

PREFIX = "playwright"
ExecType = Literal["NewPage"]

X = "zed_scrapy_playwright.handler.PlaywrightDownloaderMiddleware"


class Response(scrapy.http.Response):
    def __init__(
        self,
        result,
        url=f"{PREFIX}://response",
        status=200,
        headers=None,
        body=b"",
        flags=None,
        request=None,
        certificate=None,
        ip_address=None,
        protocol=None,
    ):
        super().__init__(
            url,
            status,
            headers,
            body,
            flags,
            request,
            certificate,
            ip_address,
            protocol,
        )
        self.result: Any = result


class Request(scrapy.Request):
    def __init__(
        self,
        exec_type: ExecType = "NewPage",
        execution: Callable[["Request", Page], Awaitable[Any]] | None = None,
        callback=None,
        # method="GET",
        # headers=None,
        # body=None,
        # cookies=None,
        meta=None,
        # encoding="utf-8",
        # priority=0,
        dont_filter=True,
        # errback=None,
        # flags=None,
        # cb_kwargs=None,
    ):
        super().__init__(
            url=f"{PREFIX}://{exec_type}",
            callback=callback,
            # method,
            # headers,
            # body,
            # cookies,
            meta=meta,
            # encoding,
            # priority,
            dont_filter=dont_filter,
            # errback,
            # flags,
            # cb_kwargs,
        )
        self.exec_type: ExecType = exec_type
        self.execution = execution if execution else self._default_execution

    @staticmethod
    async def _default_execution(request: "Request", page: Page):
        print("Warning")


class Spider(scrapy.Spider):
    """用以判断是否启用此对应中间件的环境"""

    info = {"headless": False, "executable_path": None}

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any) -> Self:
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)

        if X not in spider.settings.getdict("DOWNLOADER_MIDDLEWARES"):
            raise NotConfigured(
                f"没有注册 {X}, 则不能启用该中间件及其对应的爬虫类 {type(spider)}。"
            )

        return spider

    def __init__(self, name: str | None = None, **kwargs: dict):
        super().__init__(name, **kwargs)
