import enum
from typing import Any

import scrapy.http
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapy import Request, crawler, signals
from scrapy.exceptions import IgnoreRequest

from . import constants, pointer

# from . import definition as Zed


class PageStatus(str, enum.Enum):
    """"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name  # 返回成员名字作为值

    Unmount = enum.auto()
    Leisure = enum.auto()
    BeUsing = enum.auto()
    Cooling = enum.auto()


class PageData(str, enum.Enum):
    address = "data-address"
    status = "data-status"


print(list(PageStatus))


class Provider:
    """处理 Playwright 对象的调用"""

    def __init__(self) -> None:
        pass

    async def init(self, info):
        # 1. 创建基础容器
        self.playwright_context_manager = async_playwright()
        self.playwright = await self.playwright_context_manager.start()
        self.default_browser = await self.playwright.chromium.launch(**info)
        self.default_context = await self.default_browser.new_context(no_viewport=True)
        self.default_page = await self.default_context.new_page()
        # 2. 更新页面内容
        await self.init_home_page()
        # 3. 绑定基础变量
        await self.bind_defaults()
        # 4. 防止变量丢失
        self.objs: dict[int, Any] = {}
        for obj in [
            self.playwright,
            self.default_browser,
            self.default_context,
            self.default_page,
        ]:
            self.objs[id(obj)] = obj
        return self

    async def init_home_page(self):
        home = self.default_page
        await home.goto("about:_blank")
        h, m = pointer.content()
        await home.set_content(h)
        await home.evaluate(pointer.assets(constants.JQ4).read_text(encoding="utf-8"))
        await home.evaluate(
            # "(m) => document.querySelector('main').outerHTML = m;",
            "(m) => { $('main').replaceWith(m); }",
            m,
        )
        # scripts = await home.locator("main script").all()
        # [await home.evaluate(await s.text_content() or "") for s in scripts]

    async def bind(self, selector: str, address): ...

    async def bind_defaults(self):
        async def bind_default(selector: str, address):
            home = self.default_page
            await home.evaluate(
                """([s,v,status]) => { $(s).addClass('default').attr('data-address',v).attr('data-status', status) }""",
                [selector, id(address), PageStatus.Leisure],
            )

        await bind_default("playwright:first", self.playwright)
        await bind_default("browser:first", self.default_browser)
        await bind_default("context:first", self.default_context)
        await self.default_page.evaluate("""$('context').prepend($('<page></page>'))""")
        await bind_default("page:first", self.default_page)

    async def close(self):
        await self.default_browser.close()
        await self.playwright.stop()
        await self.playwright_context_manager.__aexit__()

    async def css(self, selector: str | None = None):
        if selector is None:
            return await self.default_context.new_page()

        elements = await self.default_page.locator(selector).all()

        # rank = [
        #     PageStatus.Leisure,
        #     PageStatus.Cooling,
        #     PageStatus.BeUsing,
        #     PageStatus.Unmount,
        #     None,
        # ]

        # def sort_(e):
        #     status = asyncioe.get_attribute(PageData.status)
        #     return rank.index(status)

        # elements.sort(key=sort_)
        address: str | None = None

        for e in elements:  # TODO 这里的排队逻辑有待理清
            status = await e.get_attribute(PageData.status)

            match status:
                case None:
                    ...
                case PageStatus.Unmount:
                    ...
                case PageStatus.Leisure:
                    address = await e.get_attribute(PageData.address)

                case PageStatus.BeUsing:
                    ...
                case PageStatus.Cooling:
                    ...

        if address is None:
            raise ValueError()

        if obj := self.objs.get(int(address)):
            return obj
        else:
            raise KeyError()
