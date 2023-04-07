import typing as t
from dataclasses import dataclass
from functools import wraps
from json import JSONDecodeError
from subprocess import list2cmdline

import uiautomator2 as u2
from adbutils import AdbError

from module.device.connection import Connection
from module.device.method.utils import RETRY_TRIES, retry_sleep, handle_adb_error, possible_reasons, \
    PackageNotInstalled, ImageTruncated
from module.exception import RequestHumanTakeover
from module.logger import logger


@dataclass
class ProcessInfo:
    pid: int
    ppid: int
    thread_count: int
    cmdline: str
    name: str


@dataclass
class ShellBackgroundResponse:
    success: bool
    pid: int
    description: str


def retry(func):
    @wraps(func)
    def retry_wrapper(self, *args, **kwargs):
        """
        Args:
            self (Uiautomator2):
        """
        init = None
        for _ in range(RETRY_TRIES):
            try:
                if callable(init):
                    retry_sleep(_)
                    init()

                return func(self, *args, **kwargs)
            # Can't handle
            except RequestHumanTakeover:
                break
            # When adb server was killed
            except ConnectionResetError as e:
                logger.error(e)

                def init():
                    self.adb_reconnect()
            # In `device.set_new_command_timeout(604800)`
            # json.decoder.JSONDecodeError: Expecting value: line 1 column 2 (char 1)
            except JSONDecodeError as e:
                logger.error(e)

                def init():
                    self.install_uiautomator2()
            # AdbError
            except AdbError as e:
                if handle_adb_error(e):
                    def init():
                        self.adb_reconnect()
                else:
                    break
            # RuntimeError: USB device 127.0.0.1:5555 is offline
            except RuntimeError as e:
                if handle_adb_error(e):
                    def init():
                        self.adb_reconnect()
                else:
                    break
            # In `assert c.read string(4) == _OKAY`
            # ADB on emulator not enabled
            except AssertionError as e:
                logger.exception(e)
                possible_reasons(
                    'If you are using BlueStacks or LD player or WSA, '
                    'please enable ADB in the settings of your emulator'
                )
                break
            # Package not installed
            except PackageNotInstalled as e:
                logger.error(e)

            # ImageTruncated
            except ImageTruncated as e:
                logger.error(e)

                def init():
                    pass
            # Unknown
            except Exception as e:
                logger.exception(e)

                def init():
                    pass

        logger.critical(f'Retry {func.__name__}() failed')
        raise RequestHumanTakeover

    return retry_wrapper


class Uiautomator2(Connection):

    def resolution_uiautomator2(self) -> t.Tuple[int, int]:
        """
        Faster u2.window_size(), cause that calls `dumpsys display` twice.

        Returns:
            (width, height)
        """
        info = self.u2.http.get('/info').json()
        w, h = info['display']['width'], info['display']['height']
        rotation = self.get_orientation()
        if (w > h) != (rotation % 2 == 1):
            w, h = h, w
        return w, h

    def resolution_check_uiautomator2(self):
        width, height = self.resolution_uiautomator2()
        logger.attr('Screen_size', f'{width}x{height}')

        if width == 720 and height == 1280:
            return (width, height)

        logger.critical(f'Resolution not supported: {width}x{height}')
        logger.critical('Please set emulator resolution to 720x1280')
        raise RequestHumanTakeover

    @retry
    def proc_list_uiautomator2(self) -> t.List[ProcessInfo]:
        """
        Get info about current processes.
        """
        resp = self.u2.http.get("/proc/list", timeout=10)
        resp.raise_for_status()
        result = [
            ProcessInfo(
                pid=proc['pid'],
                ppid=proc['ppid'],
                thread_count=proc['threadCount'],
                cmdline=' '.join(proc['cmdline']) if proc['cmdline'] is not None else '',
                name=proc['name'],
            ) for proc in resp.json()
        ]
        return result

    @retry
    def u2_shell_background(self, cmdline, timeout=10) -> ShellBackgroundResponse:
        """
        Run at background.

        Note that this function will always return a success response,
        as this is a untested and hidden method in ATX.
        """
        if isinstance(cmdline, (list, tuple)):
            cmdline = list2cmdline(cmdline)
        elif isinstance(cmdline, str):
            cmdline = cmdline
        else:
            raise TypeError("cmdargs type invalid", type(cmdline))

        data = dict(command=cmdline, timeout=str(timeout))
        ret = self.u2.http.post("/shell/background", data=data, timeout=timeout + 10)
        ret.raise_for_status()

        resp = ret.json()
        resp = ShellBackgroundResponse(
            success=bool(resp.get('success', False)),
            pid=resp.get('pid', 0),
            description=resp.get('description', '')
        )
        return resp

    @retry
    def app_current_uiautomator2(self):
        """
        Returns:
            str: Package name.
        """
        result = self.u2.app_current()
        return result['package']

    @retry
    def app_start_uiautomator2(self, package_name=None):
        if not package_name:
            package_name = self.package
        try:
            self.u2.app_start(package_name)
        except u2.exceptions.BaseError as e:
            # BaseError: package "com.proximabeta.nikke" not found
            logger.error(e)
            raise PackageNotInstalled(package_name)

    @retry
    def app_stop_uiautomator2(self, package_name=None):
        if not package_name:
            package_name = self.package
        self.u2.app_stop(package_name)
