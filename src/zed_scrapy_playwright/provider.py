from typing import Any

import scrapy.http
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapy import Request, crawler, signals

# from . import constants, pointer
# from . import definition as Zed


class Provider:
    """处理 Playwright 对象的调用"""

    def __init__(self) -> None:
        pass

    async def init(self, info):
        self.playwright_context_manager = async_playwright()
        self.playwright = await self.playwright_context_manager.start()
        self.default_browser = await self.playwright.chromium.launch(**info)
        self.default_context = await self.default_browser.new_context(no_viewport=True)
        # self.browser = await self.pr.chromium.launch(**self.c.spider.info)
        # self.context = await self.browser.new_context(no_viewport=True)
        self.objs: dict[int, Any] = {}
        return self

    async def close(self):
        await self.default_browser.close()
        await self.playwright.stop()
        await self.playwright_context_manager.__aexit__()

    async def css(self, selector: str | None = None):
        if selector is None:
            return await self.default_context.new_page()
        else:
            pass

    # async def apply(self): ...
    # async def apply_custom(self):
    #     home = self.home = await self.context.new_page()
    #     h, m = pointer.content()

    #     # 渲染html
    #     await home.set_content(h)
    #     await home.evaluate(pointer.assets(constants.JQ4).read_text(encoding="utf-8"))
    #     await home.evaluate(
    #         "(m) => document.querySelector('main').outerHTML = m;",
    #         m,
    #     )
    #     scripts = await home.locator("main script").all()
    #     [await home.evaluate(await s.text_content() or "") for s in scripts]

    #     # 加入home页面
    #     await home.evaluate("""() => {

    #         p = document.createElement('page')
    #         p.id = 'myPage';
    #         p.textContent = 'xxxxxxxxxxxxxx';
    #         document.querySelector('main context').prepend(p)
    #         }""")

    #     # 绑定

    #     # 先创建 html, 再把 address绑上去。
    #     async def bind(selector, obj):
    #         await home.evaluate(
    #             """([selector, x]) => { $(selector).data.address = x }""",
    #             [selector, id(obj)],
    #         )

    #     await bind("playwright:first", self.pm)
