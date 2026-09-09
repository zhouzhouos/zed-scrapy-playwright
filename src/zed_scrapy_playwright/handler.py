# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


import scrapy.http
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapy import Request, crawler, signals
from scrapy.exceptions import IgnoreRequest

from . import definition as Zed
from . import provider


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
        if isinstance(request, Zed.Request):
            print("主动发起", request.url, request.meta)

            page = await self.provider.css(request.selector)

            if page is None:
                raise IgnoreRequest(f"{request.selector} 没有对象")

            if request.meta.get("no-stealth") is None:
                print("已为 new page 自动施加 Stealth.apply_stealth_async")
                await Stealth().apply_stealth_async(page)

            ret = await request.execution(Zed.ExecParam(request, page))

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

            return Zed.Response(ret, request=request)

        # 这里处理自动发起的 scrapy.Request 类型，比如 <class 'scrapy.http.request.Request'> wpwp://nothing/robots.txt
        if request.url.startswith(Zed.PREFIX):
            print("自动请求", request.url, "已拦截")
            return Zed.Response("", request=request)

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

    async def spider_opened(self, spider=None):
        self.c: crawler.Crawler
        # if not isinstance(self.c.spider, Zed.Spider):
        #     print(
        #         f"Warning: 该爬虫类没有继承于 {type(self)}，将不会进行此中间件环境的启用",
        #     )
        #     return
        if self.has_validate_spider:
            print("spider_opened, start the initialization of async playwright")
            self.provider = await provider.Provider().init(
                getattr(self.c.spider, "config", None)
            )

    async def spider_closed(self):
        # if not isinstance(self.c.spider, Zed.Spider):
        #     return

        if self.has_validate_spider:
            print("spider_closed, start the finalizing work of async playwright")
            await self.provider.close()
