"""从conf.html中找到配置项，再生成。"""

import sys
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, Optional, TypedDict, TypeVar, Union

T = TypeVar("T")
from playwright.async_api import Page

from zed_scrapy_playwright import constants


class TestingParams(TypedDict):
    sys_argv: list[str]


IS_DEBUGGING = True


def assets(file: str = ""):
    """获取包内 assets 文件夹的路径对象"""
    path = str(files(constants.PACKAGE_NAME) / "assets")
    return Path(path) / file


def choose[T](*args: T) -> T | None:
    """以输入顺序为优先级顺序"""
    for x in args:
        if not x is None:
            return x


def check(*, _testing_params: TestingParams | None = None):
    """检查配置可用性，并返回填充模板后的 html"""
    appoint: Path | None = None  # 命令行指定
    default: Path | None = None  # 根目录约定
    builtin: Path | None = None  # 模块内置的(保底)

    # 先检查命令行参数。有测试就测试，无则使用正常的 argv
    for param in sys.argv if _testing_params is None else _testing_params["sys_argv"]:
        if not param.startswith(constants.CLI_PARAM_NAME):
            continue

        _, f = param.split("=", maxsplit=1)
        file = Path(f.strip())
        if not file.is_file():
            raise FileNotFoundError(f"配置文件 {f} 不存在")

        appoint = file
        break

    # 再检查是否有默认文件
    file = Path(".") / constants.CUSTOM_HTML
    default = file if file.is_file() else None

    # 最后再使用插件内置的空白配置文件
    builtin = assets() / constants.CUSTOM_HTML

    custom = appoint if appoint else default
    custom = custom if custom else builtin

    print(
        f"本插件使用了参数 `-a {constants.CLI_PARAM_NAME}` 作为 CLI 参数，当前值为 {custom}"
    )

    return custom


def content():
    html = assets(constants.HOME_HTML).read_text(encoding="utf-8")
    main = check().read_text(encoding="utf-8")
    return html, main
