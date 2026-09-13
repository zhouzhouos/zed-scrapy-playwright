"""此处尽可能不实际导入其他本模组库，避免回环"""

# 加上它后，注解变成字符串,之后所有注解不再求值，而是原样保存为字符串
from __future__ import annotations  # 避免在注释上产生循环导入

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self, TypedDict

# from scrapy import Request
import scrapy.http
from playwright.async_api import Page, ProxySettings, async_playwright

# from scrapy.http.response import

if TYPE_CHECKING:
    from zed_scrapy_playwright import definition as Z


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

    @abstractmethod
    async def takeover(
        self, request: Z.Request
    ) -> Z.Response | scrapy.http.HtmlResponse:
        """Takeover"""
