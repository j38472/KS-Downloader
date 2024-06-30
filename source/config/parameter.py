from pathlib import Path
from typing import TYPE_CHECKING

from httpx import HTTPError
from httpx import TimeoutException
from httpx import get

from source.custom import PROJECT_ROOT
from source.variable import RETRY
from source.variable import TIMEOUT

if TYPE_CHECKING:
    from source.tools import ColorConsole
    from source.tools import Cleaner


class Parameter:
    NO_PROXY = {
        "http://": None,
        "https://": None,
    }

    def __init__(self,
                 console: "ColorConsole",
                 cleaner: "Cleaner",
                 # cookie: str,
                 folder_name: str = "Download",
                 work_path: str = "",
                 timeout=TIMEOUT,
                 max_retry=RETRY,
                 proxy: str | dict = None,
                 cover="",
                 music=False,
                 download_record: bool = True,
                 data_record: bool = False,
                 chunk=1024 * 1024,
                 folder_mode: bool = False,
                 max_workers=4,
                 ):
        self.root = PROJECT_ROOT
        self.cleaner = cleaner
        self.console = console
        self.timeout = self.__check_timeout(timeout)
        self.retry = self.__check_max_retry(max_retry)
        self.proxy = self.__check_proxy(proxy)
        self.folder_name = self.__check_folder_name(folder_name)
        self.work_path = self.__check_work_path(work_path)
        # self.cookie = self.__check_cookie(cookie)
        self.cover = self.__check_cover(cover)
        self.music = self.check_bool(music, False)
        self.download_record = self.check_bool(download_record, True)
        self.data_record = self.check_bool(data_record, False)
        self.chunk = self.__check_chunk(chunk)
        self.folder_mode = self.check_bool(folder_mode, False)
        self.max_workers = self.__check_max_workers(max_workers)

    def run(self) -> dict:
        return {
            "cleaner": self.cleaner,
            "root": self.root,
            "console": self.console,
            "timeout": self.timeout,
            "max_retry": self.retry,
            "proxy": self.proxy,
            "work_path": self.work_path,
            "folder_name": self.folder_name,
            # "cookie": self.cookie,
            "cover": self.cover,
            "music": self.music,
            "download_record": self.download_record,
            "data_record": self.data_record,
            "max_workers": self.max_workers,
            "folder_mode": self.folder_mode,
            "chunk": self.chunk,
        }

    def __check_timeout(self, timeout: int) -> int:
        if not isinstance(timeout, int) or timeout <= 0:
            self.console.warning("timeout 参数错误")
            return 10
        return timeout

    def __check_max_retry(self, max_retry: int) -> int:
        if not isinstance(max_retry, int) or max_retry < 0:
            self.console.warning("max_retry 参数错误")
            return 5
        return max_retry

    def __check_max_workers(self, max_workers: int) -> int:
        if isinstance(max_workers, int) and max_workers > 0:
            return max_workers
        self.console.warning("max_workers 参数错误")
        return 4

    def __check_proxy(
            self,
            proxy: str | dict,
            url="https://www.baidu.com/") -> dict:
        if not proxy:
            return {"proxies": self.NO_PROXY}
        if isinstance(proxy, str):
            kwarg = {"proxy": proxy}
        elif isinstance(proxy, dict):
            kwarg = {"proxies": proxy}
        else:
            self.console.warning(f"proxy 参数 {proxy} 设置错误，程序将不会使用代理", )
            return {"proxies": self.NO_PROXY}
        try:
            response = get(
                url,
                **kwarg, )
            response.raise_for_status()
            self.console.info(f"代理 {proxy} 测试成功")
            return kwarg
        except TimeoutException:
            self.console.warning(f"代理 {proxy} 测试超时")
        except HTTPError as e:
            self.console.warning(f"代理 {proxy} 测试失败：{e}")
        return {"proxies": self.NO_PROXY}

    def __check_work_path(self, work_path: str) -> Path:
        if not work_path:
            return self.root
        if (r := Path(work_path)).is_dir():
            return r
        if r := self.__check_root_again(r):
            return r
        self.console.warning("work_path 参数不是有效的文件夹路径，程序将使用项目根路径作为储存路径")
        return self.root

    @staticmethod
    def __check_root_again(root: Path) -> bool | Path:
        if root.resolve().parent.is_dir():
            root.mkdir()
            return root
        return False

    def __check_folder_name(self, folder_name: str) -> str:
        if n := self.cleaner.filter_name(folder_name, ""):
            return n
        self.console.warning("folder_name 参数不是有效的文件夹名称，程序将使用默认值：Download")
        return "Download"

    def __check_cookie(self, cookie: str) -> str:
        if isinstance(cookie, str):
            return cookie
        self.console.warning("cookie 参数错误")
        return ""

    def __check_cover(self, cover: str) -> str:
        if (c := cover.upper()) in {"", "JPEG", "WEBP"}:
            return c
        self.console.warning("cover 参数错误")
        return ""

    @staticmethod
    def check_bool(value: bool, default: bool) -> bool:
        return value if isinstance(value, bool) else default

    def __check_chunk(self, chunk: int) -> int:
        if isinstance(chunk, int) and chunk > 1024:
            return chunk
        self.console.warning("chunk 参数错误")
        return 1024 * 1024
