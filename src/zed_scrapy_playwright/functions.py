import logging

# from collections.abc import Awaitable, Callable
# from dataclasses import dataclass
from functools import wraps

# from typing import Any, Literal, Self, Type
import scrapy

# import scrapy.http
# from playwright.async_api import Page
from zed_scrapy_playwright import constants as C
from zed_scrapy_playwright.interface import ConfigDict


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


def enable(config: ConfigDict | None = None):
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
