# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


import importlib.util
import logging
from typing import cast

import scrapy.http
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapy import Request, crawler, signals
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.log import SpiderLoggerAdapter

from zed_scrapy_playwright import constants
from zed_scrapy_playwright import definition as Z
from zed_scrapy_playwright import interface as I
from zed_scrapy_playwright.provider import DefaultProvider

# HAS_SCHEDULE_MODULE = importlib.util.find_spec("zed_sp_schedule") is not None
# HAS_TRANSLATE_MODULE = importlib.util.find_spec("zed_sp_translate") is not None

# if HAS_SCHEDULE_MODULE:
#     import zed_sp_schedule
# if HAS_TRANSLATE_MODULE:
#     import zed_sp_translate

HAS_SCHEDULE_MODULE = False
HAS_TRANSLATE_MODULE = False


class PlaywrightDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler: crawler.Crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        s.c = crawler
        # 连接中间件在爬虫开始时的触发事件
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # 连接中间件在爬虫结束时的触发事件
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    async def process_request(self, request: Request, spider=None):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        # 这里处理主动发起的自定义的 request 类型
        if isinstance(request, Z.Request):
            self.logger.info(f"主动请求 {request.url} with {request.meta}")
            response = await self.provider.takeover(request)
            return response

        # 这里处理自动发起的 scrapy.Request 类型，比如 <class 'scrapy.http.request.Request'> wpwp://nothing/robots.txt
        if request.url.startswith(Z.C.REQUEST_PREFIX):
            self.logger.info(f"自动请求 {request.url} 已被拦截")
            return Z.Response("", request=request)

        # 当请求不是zsp的request类时，考虑兼容性
        if self.has_validate_spider:
            ...

        # 其他的寻常的 request 不在这里截留，让其 continue

    def process_response(self, request, response, spider=None):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider=None):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    @property
    def has_validate_spider(self):
        return hasattr(self.c.spider, "config")

    # @property
    # def provider(self):
    #     return self._provider

    # @provider.setter
    # def provider(self, x: I.Provider):
    #     self._provider = x

    async def spider_opened(self, spider=None):
        self.c: crawler.Crawler
        # if not isinstance(self.c.spider, Zed.Spider):
        #     print(
        #         f"Warning: 该爬虫类没有继承于 {type(self)}，将不会进行此中间件环境的启用",
        #     )
        #     return
        if not self.has_validate_spider:
            return

        self.logger.info("spider_opened, start the initialization of async playwright")

        # create the resource provider
        CustomProvider = (
            DefaultProvider if not HAS_SCHEDULE_MODULE else zed_sp_schedule.Provider
        )

        if config_dictionary := getattr(self.c.spider, "config", None):
            info = cast(I.ConfigDict, config_dictionary)
            self.provider = await CustomProvider(info).start()
        else:
            self.provider = await DefaultProvider(None).start()

        self.logger.warning(f"{type(self.provider)}")

        # create the method translator
        if HAS_TRANSLATE_MODULE:
            ...

    @property
    def logger(self) -> SpiderLoggerAdapter:
        # name = self.c.spider.name if self.c.spider else "ZSP"
        logger = logging.getLogger(constants.PACKAGE_NAME)
        return SpiderLoggerAdapter(logger, {"zed-sp-middleware": self})

    async def spider_closed(self):
        # if not isinstance(self.c.spider, Zed.Spider):
        #     return

        if self.has_validate_spider:
            self.logger.info(
                "spider_closed, start the finalizing work of async playwright"
            )
            await self.provider.close()
