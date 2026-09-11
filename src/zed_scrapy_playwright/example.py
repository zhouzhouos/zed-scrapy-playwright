# from asyncio import sleep

import scrapy.http

import zed_scrapy_playwright as zsp


# 配置并自检
@zsp.enable({"headless": False, "executable_path": "/opt/google/chrome/chrome"})
class ExampleExecutor(scrapy.Spider):
    name = "example"
    # allowed_domains = ["example.com"]
    # start_urls = ["https://example.com"]

    async def start(self):
        self.logger.info(f"自检结果 {zsp.validate(self)}")

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
        print(f"parse2: {response.url}")

    def parse(self, response: zsp.Response):
        print(f"parse1: {response.result}")

    @staticmethod
    async def exection3(ep: zsp.ExecParam):
        # await sleep(20)
        pass

    def parse3(self, response: scrapy.http.HtmlResponse):
        print(f"parse3: {response.url}")
        print(f"parse3: pages: {response.css('page').getall()}")
