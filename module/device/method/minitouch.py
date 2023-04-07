import json
import socket
import time
from functools import cached_property, wraps
from typing import List

import websockets
from adbutils import AdbError

from module.base.decorator import del_cached_property
from module.base.timer import Timer
from module.device.connection import Connection
from module.device.method.utils import RETRY_TRIES, retry_sleep, handle_adb_error
from module.exception import RequestHumanTakeover, ScriptError
from module.logger import logger


class MinitouchOccupiedError(Exception):
    pass


class MinitouchNotInstalledError(Exception):
    pass


def retry(func):
    @wraps(func)
    def retry_wrapper(self, *args, **kwargs):
        """
        Args:
            self (Minitouch):
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
            # Emulator closed
            except ConnectionAbortedError as e:
                logger.error(e)

                def init():
                    self.adb_reconnect()
            # MinitouchNotInstalledError: Received empty data from minitouch
            except MinitouchNotInstalledError as e:
                logger.error(e)

                def init():
                    self.install_uiautomator2()
                    if self._minitouch_port:
                        self.adb_forward_remove(f'tcp:{self._minitouch_port}')
                    del_cached_property(self, 'minitouch_builder')
            # MinitouchOccupiedError: Timeout when connecting to minitouch
            except MinitouchOccupiedError as e:
                logger.error(e)

                def init():
                    self.restart_atx()
                    if self._minitouch_port:
                        self.adb_forward_remove(f'tcp:{self._minitouch_port}')
                    del_cached_property(self, 'minitouch_builder')
            # AdbError
            except AdbError as e:
                if handle_adb_error(e):
                    def init():
                        self.adb_reconnect()
                else:
                    break
            except BrokenPipeError as e:
                logger.error(e)

                def init():
                    del_cached_property(self, 'minitouch_builder')
            # Unknown, probably a trucked image
            except Exception as e:
                logger.exception(e)

                def init():
                    pass

        logger.critical(f'Retry {func.__name__}() failed')
        raise RequestHumanTakeover

    return retry_wrapper


class Command:
    def __init__(
            self,
            operation: str,
            contact: int = 0,
            x: int = 0,
            y: int = 0,
            ms: int = 10,
            pressure: int = 100
    ):
        """
        See https://github.com/openstf/minitouch#writable-to-the-socket

        Args:
            operation: c, r, d, m, u, w
            contact:
            x:
            y:
            ms:
            pressure:
        """
        self.operation = operation
        self.contact = contact
        self.x = x
        self.y = y
        self.ms = ms
        self.pressure = pressure

    def to_minitouch(self) -> str:
        """
        String that write into minitouch socket
        """
        if self.operation == 'c':
            return f'{self.operation}\n'
        elif self.operation == 'r':
            return f'{self.operation}\n'
        elif self.operation == 'd':
            return f'{self.operation} {self.contact} {self.x} {self.y} {self.pressure}\n'
        elif self.operation == 'm':
            return f'{self.operation} {self.contact} {self.x} {self.y} {self.pressure}\n'
        elif self.operation == 'u':
            return f'{self.operation} {self.contact}\n'
        elif self.operation == 'w':
            return f'{self.operation} {self.ms}\n'
        else:
            return ''

    def to_atx_agent(self, max_x=1280, max_y=720) -> str:
        """
        Dict that send to atx-agent, $DEVICE_URL/minitouch
        See https://github.com/openatx/atx-agent#minitouch%E6%93%8D%E4%BD%9C%E6%96%B9%E6%B3%95
        """
        x, y = self.x / max_x, self.y / max_y
        if self.operation == 'c':
            out = dict(operation=self.operation)
        elif self.operation == 'r':
            out = dict(operation=self.operation)
        elif self.operation == 'd':
            out = dict(operation=self.operation, index=self.contact, pressure=self.pressure, xP=x, yP=y)
        elif self.operation == 'm':
            out = dict(operation=self.operation, index=self.contact, pressure=self.pressure, xP=x, yP=y)
        elif self.operation == 'u':
            out = dict(operation=self.operation, index=self.contact)
        elif self.operation == 'w':
            out = dict(operation=self.operation, milliseconds=self.ms)
        else:
            out = dict()
        return json.dumps(out)


class CommandBuilder:
    DEFAULT_DELAY = 0.05
    max_x = 1280
    max_y = 720

    def __init__(self, device):
        """
        Args:
            device:
        """
        self.device = device
        self.commands = []
        self.delay = 0

    def convert(self, x, y):
        max_x, max_y = self.device.max_x, self.device.max_y
        orientation = self.device.orientation
        if orientation == 0:
            pass
        elif orientation == 1:
            x, y = 720 - y, x
            max_x, max_y = max_y, max_x
        elif orientation == 2:
            x, y = 1280 - x, 720 - y
        elif orientation == 3:
            x, y = y, 1280 - x
            max_x, max_y = max_y, max_x
        else:
            raise ScriptError(f'Invalid device orientation: {orientation}')

        self.max_x, self.max_y = max_x, max_y
        x, y = int(x / 1280 * max_x), int(y / 720 * max_y)
        return x, y

    def commit(self):
        """ add minitouch command: 'c\n' """
        self.commands.append(Command('c'))
        return self

    def reset(self):
        """ add minitouch command: 'r\n' """
        self.commands.append(Command('r'))
        return self

    def wait(self, ms=10):
        """ add minitouch command: 'w <ms>\n' """
        self.commands.append(Command('w', ms=ms))
        self.delay += ms
        return self

    def up(self, contact=0):
        """ add minitouch command: 'u <contact>\n' """
        self.commands.append(Command('u', contact=contact))
        return self

    def down(self, x, y, contact=0, pressure=100):
        """ add minitouch command: 'd <contact> <x> <y> <pressure>\n' """
        x, y = self.convert(x, y)
        self.commands.append(Command('d', x=x, y=y, contact=contact, pressure=pressure))
        return self

    def move(self, x, y, contact=0, pressure=100):
        """ add minitouch command: 'm <contact> <x> <y> <pressure>\n' """
        x, y = self.convert(x, y)
        self.commands.append(Command('m', x=x, y=y, contact=contact, pressure=pressure))
        return self

    def clear(self):
        """ clear current commands """
        self.commands = []
        self.delay = 0

    def to_minitouch(self) -> str:
        return ''.join([command.to_minitouch() for command in self.commands])

    def to_atx_agent(self) -> List[str]:
        return [command.to_atx_agent(self.max_x, self.max_y) for command in self.commands]


class Minitouch(Connection):
    _minitouch_port: int = 0
    _minitouch_client: socket.socket
    _minitouch_pid: int
    _minitouch_ws: websockets.WebSocketClientProtocol
    max_x: int
    max_y: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def minitouch_builder(self):
        self.minitouch_init()
        return CommandBuilder(self)

    def minitouch_init(self):
        logger.hr('MiniTouch init')
        max_x, max_y = 1280, 720
        max_contacts = 2
        max_pressure = 50
        self.get_orientation()
        """
            通过socket操作minitouch
        """
        self._minitouch_port = self.adb_forward("localabstract:minitouch")

        retry_timeout = Timer(2).start()
        while 1:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1)
            client.connect(('127.0.0.1', self._minitouch_port))
            self._minitouch_client = client

            # get minitouch server info
            socket_out = client.makefile()

            # v <version>
            # protocol version, usually it is 1. needn't use this
            try:
                out = socket_out.readline().replace("\n", "").replace("\r", "")
            except socket.timeout:
                client.close()
                raise MinitouchOccupiedError(
                    'Timeout when connecting to minitouch, '
                    'probably because another connection has been established'
                )
            logger.info(out)

            # ^ <max-contacts> <max-x> <max-y> <max-pressure>
            out = socket_out.readline().replace("\n", "").replace("\r", "")
            logger.info(out)

            try:
                _, max_contacts, max_x, max_y, max_pressure, *_ = out.split(" ")
                break
            except ValueError:
                client.close()
                if retry_timeout.reached():
                    raise MinitouchNotInstalledError(
                        'Received empty data from minitouch, '
                        'probably because minitouch is not installed'
                    )
                else:
                    # Minitouch may not start that fast
                    self.sleep(1)
                    continue

        # self.max_contacts = max_contacts
        self.max_x = int(max_x)
        self.max_y = int(max_y)
        # self.max_pressure = max_pressure

        # $ <pid>
        out = socket_out.readline().replace("\n", "").replace("\r", "")
        logger.info(out)
        _, pid = out.split(" ")
        self._minitouch_pid = pid

        logger.info(
            "minitouch running on port: {}, pid: {}".format(self._minitouch_port, self._minitouch_pid)
        )
        logger.info(
            "max_contact: {}; max_x: {}; max_y: {}; max_pressure: {}".format(
                max_contacts, max_x, max_y, max_pressure
            )
        )

    def minitouch_send(self):
        content = self.minitouch_builder.to_minitouch()
        # logger.info("send operation: {}".format(content.replace("\n", "\\n")))
        byte_content = content.encode('utf-8')
        self._minitouch_client.sendall(byte_content)
        self._minitouch_client.recv(0)
        time.sleep(self.minitouch_builder.delay / 1000 + self.minitouch_builder.DEFAULT_DELAY)
        self.minitouch_builder.clear()

    @retry
    def click_minitouch(self, x, y):
        builder = self.minitouch_builder
        builder.down(int(x * 2 * 0.9), int(y / 2 * 1.12)).commit()
        builder.up().commit()
        self.minitouch_send()
