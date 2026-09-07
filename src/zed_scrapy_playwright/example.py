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

    @staticmethod
    async def exection(request: zsp.Request, page: Page):
        await page.goto("https://example.com")
        return await page.content()

    def parse(self, response: zsp.Response):
        print(response.result)
