# zed-scrapy-playwright

> Less meta config, more Python code.

> 把 Scrapy 变成 Playwright 的事件调度引擎。

[English](docs/README-en.md)

---

## 简介

`zed-scrapy-playwright` 是一个 Scrapy 中间件，它重新定义了 Scrapy 与 Playwright 的集成方式——**让 Scrapy 成为事件调度器，让 Playwright 成为可编程的执行引擎。**

不同于传统方案将每个请求限制为单次页面导航，本中间件允许你在一个 `execution` 中完成完整的业务流程：登录、搜索、详情、下单，一气呵成。

---

## 核心特性

- **会话级控制** — 单次 execution 内多次 `goto`，登录态自动保持
- **线性编码** — 复杂流程写在一个函数里，告别 callback 地狱
- **精准数据传输** — 在 Page 中直接提取初筛数据，避免传输冗余 HTML
- **完全开放** — 任意 Playwright API 均可使用，无预定义操作限制
- **双向交叉检查** — 中间件与爬虫相互验证，配置错误快速失败
- **Stealth 灵活可控** — 可全局注入，也可在每个 execution 中自定义
- **类型安全** — 完整的类型提示，IDE 友好

---

## 快速开始

### 安装

```bash
pip install zed-scrapy-playwright
```

### 配置 settings.py

```python
DOWNLOADER_MIDDLEWARES = {
    "zed_scrapy_playwright.handler.PlaywrightDownloaderMiddleware": 300,
}
```

### 编写爬虫

```python
import zed_scrapy_playwright as zsp
from playwright.async_api import Page

class MySpider(zsp.Spider):
    name = "example"

    async def start(self):
        yield zsp.Request(
            exec_type="NewPage",
            execution=self.search_and_scrape,
            callback=self.parse,
            meta={"keyword": "laptop"},
        )

    @staticmethod
    async def search_and_scrape(request: zsp.Request, page: Page):
        keyword = request.meta["keyword"]

        await page.goto("https://example.com")
        await page.fill("#search", keyword)
        await page.click("#search-btn")
        await page.wait_for_selector(".results")

        # 初筛数据：直接在页面中提取
        items = await page.evaluate("""
            Array.from(document.querySelectorAll('.item')).map(el => ({
                title: el.querySelector('.title')?.innerText,
                price: el.querySelector('.price')?.innerText,
            }))
        """)

        return {"items": items, "keyword": keyword}

    async def parse(self, response: zsp.Response):
        data = response.data  # 初筛数据
        for item in data["items"]:
            yield {
                "title": item["title"],
                "price": float(item["price"].replace("$", "")),
            }
```

---

## 对比 scrapy-playwright

| 维度 | scrapy-playwright | zed-scrapy-playwright |
|------|:---:|:---:|
| 操作自由度 | 有限 | 无限 |
| 多次 goto | ❌ | ✅ |
| 登录态保持 | 配置复杂 | 天然支持 |
| 代码组织 | 分散 callback | 线性聚合 |
| 数据传输 | 完整 HTML | 初筛数据 |
| 防误用机制 | 无 | 双向交叉检查 |

---

## 许可证

暂定：MIT
