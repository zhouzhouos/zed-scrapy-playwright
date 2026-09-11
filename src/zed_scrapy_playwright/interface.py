"""此处不导入其他本模组库，避免回环"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import Literal, Self, TypedDict

from playwright.async_api import Page, ProxySettings


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

    @abstractmethod
    async def start(self, info: ConfigDict | None) -> Self: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def css(self, selector: str | None) -> Page | None: ...
