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

    @staticmethod
    async def exection(request: zsp.Request, page: Page):
        await page.goto("https://example.com")
        return {"info": "any"}

    @staticmethod
    async def exection2(request: zsp.Request, page: Page):
        await page.goto("https://example.com")

    def parse2(self, response: scrapy.http.HtmlResponse):
        print("parse2:", response.url)

    def parse(self, response: zsp.Response):
        print("parse:", response.result)
