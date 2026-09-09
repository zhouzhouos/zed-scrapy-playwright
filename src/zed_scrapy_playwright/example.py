from asyncio import sleep

import scrapy.http
from playwright.async_api import Page

import zed_scrapy_playwright as zsp


class ExampleExecutor(zsp.Spider):
    name = "example"
    info = {"headless": False, "executable_path": "/opt/google/chrome/chrome"}
    # allowed_domains = ["example.com"]
    # start_urls = ["https://example.com"]

    async def start(self):

        yield zsp.Request(
            execution=self.exection,
            callback=self.parse,
        )

        yield zsp.Request(
            execution=self.exection2,
            callback=self.parse2,
        )

        yield zsp.Request(
            selector="page.default",
            execution=self.exection3,
            callback=self.parse3,
        )

    @staticmethod
    async def exection(ep: zsp.ExecParam):
        await ep.page.goto("https://example.com")
        return {"info": "information"}

    @staticmethod
    async def exection2(ep: zsp.ExecParam):
        await ep.page.goto("https://example.com")
        # while not ep.page.is_closed():
        #     await sleep(1)

    def parse2(self, response: scrapy.http.HtmlResponse):
        print("parse2:", response.url)

    def parse(self, response: zsp.Response):
        print("parse:", response.result)

    @staticmethod
    async def exection3(ep: zsp.ExecParam):
        # await sleep(20)
        pass

    def parse3(self, response: scrapy.http.HtmlResponse):
        print("parse3:", response.url)
        print("parse3:", response.css("page").getall())
