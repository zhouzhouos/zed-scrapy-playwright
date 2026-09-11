# from scrapy.http import Response, TextResponse
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps

# from typing import Any, Literal, Self, Type
import scrapy
import scrapy.http
from playwright.async_api import Page

from zed_scrapy_playwright import constants as C
from zed_scrapy_playwright.interface import ConfigDict

# from scrapy.crawler import Crawler
# from scrapy.exceptions import NotConfigured
# from scrapy.signals import scheduler_empty


class Response(scrapy.http.Response):
    def __init__(
        self,
        result,
        url=f"{C.REQUEST_PREFIX}://response",
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
        self.result = result


@dataclass
class ExecParam:
    request: "Request"
    page: Page


Exection = Callable[[ExecParam], Awaitable]


class Request(scrapy.Request):
    def __init__(
        self,
        *,
        selector: str | None = None,
        execution: Exection,
        callback,
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
            url=f"{C.REQUEST_PREFIX}://request",
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
        self.selector = selector
        self.execution: Exection = execution


# class Spider(scrapy.Spider):
#     """用以判断是否启用此对应中间件的环境"""

#     info = {"headless": False, "executable_path": None}

#     @classmethod
#     def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any) -> Self:
#         spider = cls(*args, **kwargs)
#         spider._set_crawler(crawler)

#         if X not in spider.settings.getdict("DOWNLOADER_MIDDLEWARES"):
#             raise NotConfigured(
#                 f"没有注册 {X}, 则不能启用该中间件及其对应的爬虫类 {type(spider)}。"
#             )

#         return spider

#     def __init__(self, name: str | None = None, **kwargs: dict):
#         super().__init__(name, **kwargs)


def validate(spider: scrapy.Spider):
    logger = logging.getLogger(C.PACKAGE_NAME)
    X = C.MIDDLEWARE_NAME
    if X not in spider.settings.getdict("DOWNLOADER_MIDDLEWARES"):
        s = f"没有注册 {X}, 则不能启用该中间件及其对应的爬虫类 {type(spider)}。"
        logger.warning(s)
        return False
    else:
        logger.info(f"已经注册 {X}")
        return True


def enable(config: ConfigDict):
    def _enable(Spider: type[scrapy.Spider]):
        _start = Spider.start

        @wraps(_start)
        async def start(self, *args, **kwargs):
            validate(self)
            async for x in _start(self, *args, **kwargs):
                yield x

        Spider.start = start
        Spider.config = config  # type: ignore
        return Spider

    return _enable
