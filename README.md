# zed-scrapy-playwright (zsp)

> Less meta config, more Python code.    把 Scrapy 变成 Playwright 的事件调度引擎。

`zsp` 是一个 Scrapy 与 Playwright 的集成中间件，提供**会话级控制**、**线性编码**和**精准数据传输**，让你在 Scrapy 爬虫中轻松使用 Playwright 的浏览器自动化能力。

---

## ✨ 核心特性

- **会话级控制**：单次 `execution` 内支持多次 `page.goto()`，保持页面状态
- **线性编码**：告别 callback 地狱，以同步风格编写异步浏览器操作
- **精准数据传输**：直接在 Page 对象中提取数据，无需额外的解析步骤
- **完整的类型提示**：享受 IDE 智能补全和类型检查
- **装饰器启用模式**（v0.2.0+）：使用 `@zsp.enable()` 装饰器，支持任意爬虫类
- **内置 Playwright Provider**（v0.2.0+）：管理浏览器生命周期，支持 CSS 选择模式
- **Stealth 反检测**：自动注入 `playwright-stealth`，降低被识别为机器人的风险

---

## 📦 安装

```bash
pip install zed-scrapy-playwright
```

或使用 uv（推荐）：

```bash
uv add zed-scrapy-playwright
```

**安装浏览器驱动**（首次使用需要）：

```bash
playwright install
```

---

## 🚀 快速开始

### 1. 启用中间件

在 `settings.py` 中添加：

```python
DOWNLOADER_MIDDLEWARES = {
    'zsp.handler.PlaywrightDownloaderMiddleware': 543,
}
```

### 2. 编写爬虫（使用装饰器模式）

```python
import scrapy
import zsp

@zsp.enable()
class MySpider(scrapy.Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def start_requests(self):
        yield zsp.Request(
            url="https://example.com",
            callback=self.parse,
            execution=self.execution_func,
        )

    async def execution_func(self, page, request):
        await page.goto(request.url)
        content = await page.content()
        return {
            "title": await page.title(),
            "html": content,
        }

    async def parse(self, response: zsp.Response):
        print("parse:", response.result)
```

### 3. 运行爬虫

```bash
scrapy crawl my_spider
```

---

## 📖 API 文档

### `zsp.enable()`
装饰器，用于启用爬虫的 Playwright 支持。

```python
@zsp.enable()
class MySpider(scrapy.Spider):
    ...
```

### `zsp.Request`
继承自 `scrapy.Request`，增加以下参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `execution` | Callable | 异步执行函数，接收 `(page, request)` |
| `selector` | str | CSS 选择器（v0.2.0+，配合 Provider 使用） |

### `zsp.execution` 函数签名
```python
async def execution_func(page: Page, request: Request) -> dict | None:
    # 进行浏览器操作...
    return {"key": value}
```

- 返回 `None` 时，默认返回 `HtmlResponse`（页面源码）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/amazing`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 **Apache License 2.0** 许可证。

版权所有 © 2026 zhouzhouos

---

## 🧩 相关链接

- [Scrapy 官方文档](https://docs.scrapy.org/)
- [Playwright Python 官方文档](https://playwright.dev/python/)
