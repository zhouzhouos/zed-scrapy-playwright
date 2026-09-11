"""此处不导入其他本模组库，避免回环"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import Literal, Self, TypedDict

from playwright.async_api import Page, ProxySettings, async_playwright


class ChromeBrowserLaunchParameters(TypedDict, total=False):
    executable_path: Path | str | None
    channel: str | None
    args: Sequence[str] | None
    ignore_default_args: bool | Sequence[str] | None
    handle_sigint: bool | None
    handle_sigterm: bool | None
    handle_sighup: bool | None
    timeout: float | timedelta | None
    env: dict[str, str | float | bool] | None
    headless: bool | None
    proxy: ProxySettings | None
    downloads_path: Path | str | None
    slow_mo: float | None
    traces_dir: Path | str | None
    artifacts_dir: Path | str | None
    chromium_sandbox: bool | None
    firefox_user_prefs: dict[str, str | float | bool] | None


class ConfigDict(TypedDict):
    browser_type: Literal["chrome", "edge", "firefox"]
    chrome_params: ChromeBrowserLaunchParameters


class Provider(ABC):
    """处理 Playwright 对象的调用"""

    def __init__(self, info: ConfigDict | None) -> None:
        super().__init__()
        if info:
            self.config = info

    @abstractmethod
    async def start(self) -> Self:
        """Start"""

    @abstractmethod
    async def close(self) -> None:
        """Close"""

    @abstractmethod
    async def css(self, selector: str | None) -> Page | None:
        """Choose"""


class DefaultProvider(Provider):
    """moren"""

    async def start(self):
        self.playwright_context_manager = async_playwright()
        self.playwright = await self.playwright_context_manager.start()
        self.default_browser = await self.playwright.chromium.launch()
        self.default_context = await self.default_browser.new_context()
        return self

    async def close(self):
        await self.default_context.close()
        await self.default_browser.close()
        await self.playwright.stop()
        await self.playwright_context_manager.__aexit__()

    async def css(self, selector) -> Page | None:
        """Choose"""
        return await self.default_context.new_page()
