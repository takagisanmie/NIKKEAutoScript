import logging
import re
import subprocess
import time
from functools import wraps

import uiautomator2 as u2
from adbutils import AdbError, AdbDevice, AdbClient, ForwardItem

from module.base.decorator import del_cached_property
from module.base.utils import ensure_time
from module.device.connection_attr import ConnectionAttr
from module.device.method.utils import RETRY_TRIES, RETRY_DELAY, PackageNotInstalled, get_serial_pair, possible_reasons, \
    handle_adb_error, recv_all, remove_shell_warning, random_port
from module.exception import RequestHumanTakeover, EmulatorNotRunningError
from module.logger import logger
from module.map.map_grids import SelectedGrids


def retry(func):
    @wraps(func)
    def retry_wrapper(self, *args, **kwargs):
        """
        Args:
            self (Adb):
        """
        init = None
        for _ in range(RETRY_TRIES):
            try:
                if callable(init):
                    self.sleep(RETRY_DELAY)
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
            # AdbError
            except AdbError as e:
                if handle_adb_error(e):
                    def init():
                        self.adb_reconnect()
                else:
                    break

            # Package not installed
            except PackageNotInstalled as e:
                logger.error(e)
                # def init():
                #     self.detect_package()
            # Unknown, probably a trucked image
            except Exception as e:
                logger.exception(e)

                def init():
                    pass

        logger.critical(f'Retry {func.__name__}() failed')
        raise RequestHumanTakeover

    return retry_wrapper


class AdbDeviceWithStatus(AdbDevice):
    def __init__(self, client: AdbClient, serial: str, status: str):
        self.status = status
        super().__init__(client, serial)

    def __str__(self):
        return f'AdbDevice({self.serial}, {self.status})'

    __repr__ = __str__

    def __bool__(self):
        return True


class Connection(ConnectionAttr):
    def __init__(self, config):
        """
           Args:
               config (AzurLaneConfig, str): Name of the user config under ./config
           """
        super().__init__(config)
        self.detect_device()

        # Connect
        self.adb_connect(self.serial)
        logger.attr('AdbDevice', self.adb)

        # Package
        self.package = self.config.Emulator_PackageName.replace('_', '.')

        logger.attr('PackageName', self.package)

    def detect_device(self):
        """
            侦测可用的安卓设备
        """
        logger.hr('Detect device')
        logger.info('Here are the available devices, '
                    'copy to NKAS.Emulator.Serial to use it or set NKAS.Emulator.Serial="auto"')

        devices = self.list_device()

        # Show available devices
        available = devices.select(status='device')
        for device in available:
            logger.info(device.serial)
        if not len(available):
            logger.info('No available devices')

        # Show unavailable devices if having any
        unavailable = devices.delete(available)
        if len(unavailable):
            logger.info('Here are the devices detected but unavailable')
            for device in unavailable:
                logger.info(f'{device.serial} ({device.status})')

        """
            当 serial=='auto' 和 只有一个可用设备被找到时
        """
        # Auto device detection
        if self.config.Emulator_Serial == 'auto':
            if available.count == 0:
                logger.critical('No available device found, auto device detection cannot work, '
                                'please set an exact serial in NKAS.Emulator.Serial instead of using "auto"')
                raise RequestHumanTakeover
            elif available.count == 1:
                logger.info(f'Auto device detection found only one device, using it')
                self.serial = devices[0].serial
                del_cached_property(self, 'adb')
            else:
                logger.critical('Multiple devices found, auto device detection cannot decide which to choose, '
                                'please copy one of the available devices listed above to NKAS.Emulator.Serial')
                raise RequestHumanTakeover

        port_serial, emu_serial = get_serial_pair(self.serial)
        if port_serial and emu_serial:
            """
                雷电模拟器默认
                emu_device: emulator-5554
                port_device: 127.0.0.1:5555
            """
            port_device = devices.select(serial=port_serial).first_or_none()
            emu_device = devices.select(serial=emu_serial).first_or_none()
            if port_device and emu_device:
                # Paired devices found, check status to get the correct one
                """
                    当同时找到两个设备时？
                """
                if port_device.status == 'device' and emu_device.status == 'offline':
                    self.serial = port_serial
                    logger.info(f'LDPlayer device pair found: {port_device}, {emu_device}. '
                                f'Using serial: {self.serial}')
                elif port_device.status == 'offline' and emu_device.status == 'device':
                    self.serial = emu_serial
                    logger.info(f'LDPlayer device pair found: {port_device}, {emu_device}. '
                                f'Using serial: {self.serial}')

            elif not devices.select(serial=self.serial):
                # Current serial not found
                if port_device and not emu_device:
                    logger.info(f'Current serial {self.serial} not found but paired device {port_serial} found. '
                                f'Using serial: {port_serial}')
                    self.serial = port_serial

                if not port_device and emu_device:
                    logger.info(f'Current serial {self.serial} not found but paired device {emu_serial} found. '
                                f'Using serial: {emu_serial}')
                    self.serial = emu_serial

    def adb_connect(self, serial):

        # 在连接前断开不需要的设备
        for device in self.list_device():
            if device.status == 'offline':
                """
                   模拟器离线
                """
                logger.warning(f'Device {serial} is offline, disconnect it before connecting')
                self.adb_disconnect(serial)
            elif device.status == 'unauthorized':
                """
                   模拟器未开启ADB调试
                """
                logger.error(f'Device {serial} is unauthorized, please accept ADB debugging on your device')
            elif device.status == 'device':
                """
                   模拟器在线
                """
                continue
            else:
                """
                   未知状态
                """
                logger.warning(f'Device {serial} is is having a unknown status: {device.status}')
        """
            跳过 emulator-* 的模拟器设备，应该会在调用 list_device 时被找到
            MuMuX似乎无法被侦测到，默认Serial为 127.0.0.1:7555
        """
        if 'emulator-' in serial:
            logger.info(f'"{serial}" is a `emulator-*` serial, skip adb connect')
            return True

        """
            似乎是安卓真机，跳过
        """
        if re.match(r'^[a-zA-Z0-9]+$', serial):
            logger.info(f'"{serial}" seems to be a Android serial, skip adb connect')
            return True

        # Try to connect
        for _ in range(3):
            msg = self.adb_client.connect(serial)
            logger.info(msg)
            if 'connected' in msg:
                # Connected to 127.0.0.1:59865
                # Already connected to 127.0.0.1:59865
                return True
            elif 'bad port' in msg:
                # bad port number '598265' in '127.0.0.1:598265'
                logger.error(msg)
                possible_reasons('Serial incorrect, might be a typo')
                raise RequestHumanTakeover
            elif '(10061)' in msg:
                # cannot connect to 127.0.0.1:55555:
                # No connection could be made because the target machine actively refused it. (10061)
                logger.info(msg)
                logger.warning('No such device exists, please restart the emulator or set a correct serial')
                raise EmulatorNotRunningError

        # Failed to connect
        logger.warning(f'Failed to connect {serial} after 3 trial, assume connected')
        self.detect_device()
        return False

    def adb_disconnect(self, serial):
        logger.debug('adb disconnect')

        msg = self.adb_client.disconnect(serial)
        if msg:
            logger.info(msg)

        del_cached_property(self, 'hermit_session')
        del_cached_property(self, 'droidcast_session')
        del_cached_property(self, 'minitouch_builder')
        del_cached_property(self, 'reverse_server')

    def adb_reconnect(self):
        """
            当没有设备被找到时，不然重新尝试连接
        """
        self.adb_restart()
        self.adb_connect(self.serial)
        self.detect_device()

        # if self.config.Emulator_AdbRestart and len(self.list_device()) == 0:
        #     self.adb_restart()
        #     self.adb_connect(self.serial)
        #     self.detect_device()
        # else:
        #     self.adb_disconnect(self.serial)
        #     self.adb_connect(self.serial)
        #     self.detect_device()

    def adb_forward(self, remote):
        """
        Do `adb forward <local> <remote>`.
        choose a random port in FORWARD_PORT_RANGE or reuse an existing forward,
        and also remove redundant forwards.

        Args:
            remote (str):
                tcp:<port>
                localabstract:<unix domain socket name>
                localreserved:<unix domain socket name>
                localfilesystem:<unix domain socket name>
                dev:<character device name>
                jdwp:<process pid> (remote only)

        Returns:
            int: Port
        """
        port = 0

        for forward in self.adb.forward_list():
            if forward.serial == self.serial and forward.remote == remote and forward.local.startswith('tcp:'):
                if not port:
                    logger.info(f'Reuse forward: {forward}')
                    port = int(forward.local[4:])
                else:
                    logger.info(f'Remove redundant forward: {forward}')
                    self.adb_forward_remove(forward.local)

        if port:
            return port
        else:
            # Create new forward
            port = random_port(self.config.FORWARD_PORT_RANGE)
            forward = ForwardItem(self.serial, f'tcp:{port}', remote)
            logger.info(f'Create forward: {forward}')
            logger.info(f'{forward.local} --> {forward.remote}')
            self.adb.forward(forward.local, forward.remote)
            return port

    def adb_push(self, local, remote):
        """
        Args:
            local (str):
            remote (str):

        Returns:
            str:
        """
        cmd = ['push', local, remote]
        return self.adb_command(cmd)

    def adb_command(self, cmd, timeout=10):
        """
        Execute ADB commands in a subprocess,
        usually to be used when pulling or pushing large files.

        Args:
            cmd (list):
            timeout (int):

        Returns:
            str:
        """
        cmd = list(map(str, cmd))
        cmd = [self.adb_binary, '-s', self.serial] + cmd
        logger.info(f'Execute: {cmd}')

        # Use shell=True to disable console window when using GUI.
        # Although, there's still a window when you stop running in GUI, which cause by gooey.
        # To disable it, edit gooey/gui/util/taskkill.py

        # No gooey anymore, just shell=False
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            logger.warning(f'TimeoutExpired when calling {cmd}, stdout={stdout}, stderr={stderr}')
        return stdout

    def adb_forward_remove(self, local):
        """
        Equivalent to `adb -s <serial> forward --remove <local>`
        More about the commands send to ADB server, see:
        https://cs.android.com/android/platform/superproject/+/master:packages/modules/adb/SERVICES.TXT

        Args:
            local (str): Such as 'tcp:2437'
        """
        with self.adb_client._connect() as c:
            list_cmd = f"host-serial:{self.serial}:killforward:{local}"
            c.send_command(list_cmd)
            c.check_okay()

    def adb_restart(self):
        """
            Reboot adb client
        """
        logger.info('Restart adb')
        # Kill current client
        self.adb_client.server_kill()
        # Init adb client
        del_cached_property(self, 'adb_client')
        _ = self.adb_client

    _orientation_description = {
        0: 'Normal',
        1: 'HOME key on the right',
        2: 'HOME key on the top',
        3: 'HOME key on the left',
    }
    orientation = 0

    def install_uiautomator2(self):
        """
        Init uiautomator2 and remove minicap.
        """
        logger.info('Install uiautomator2')
        init = u2.init.Initer(self.adb, loglevel=logging.DEBUG)
        # MuMu X has no ro.product.cpu.abi, pick abi from ro.product.cpu.abilist
        if init.abi not in ['x86_64', 'x86', 'arm64-v8a', 'armeabi-v7a', 'armeabi']:
            init.abi = init.abis[0]
        init.set_atx_agent_addr('127.0.0.1:7912')
        try:
            init.install()
        except ConnectionError:
            u2.init.GITHUB_BASEURL = 'http://tool.appetizer.io/openatx'
            init.install()
        self.uninstall_minicap()

    def uninstall_minicap(self):
        """ minicap can't work or will send compressed images on some emulators. """
        logger.info('Removing minicap')
        self.adb_shell(["rm", "/data/local/tmp/minicap"])
        self.adb_shell(["rm", "/data/local/tmp/minicap.so"])

    def restart_atx(self):
        """
        Minitouch supports only one connection at a time.
        Restart ATX to kick the existing one.
        """
        logger.info('Restart ATX')
        atx_agent_path = '/data/local/tmp/atx-agent'
        self.adb_shell([atx_agent_path, 'server', '--stop'])
        self.adb_shell([atx_agent_path, 'server', '--nouia', '-d', '--addr', '127.0.0.1:7912'])

    @retry
    def get_orientation(self):
        """
        Rotation of the phone

        Returns:
            int:
                0: 'Normal'
                1: 'HOME key on the right'
                2: 'HOME key on the top'
                3: 'HOME key on the left'
        """

        """
            检查设备方向
        """
        _DISPLAY_RE = re.compile(
            r'.*DisplayViewport{.*valid=true, .*orientation=(?P<orientation>\d+), .*deviceWidth=(?P<width>\d+), deviceHeight=(?P<height>\d+).*'
        )
        output = self.adb_shell(['dumpsys', 'display'])

        res = _DISPLAY_RE.search(output, 0)

        if res:
            o = int(res.group('orientation'))

            if o in Connection._orientation_description:
                pass
            else:
                o = 0
                logger.warning(f'Invalid device orientation: {o}, assume it is normal')
        else:
            o = 0
            logger.warning('Unable to get device orientation, assume it is normal')

        self.orientation = o
        logger.attr('Device Orientation', f'{o} ({Connection._orientation_description.get(o, "Unknown")})')
        return o

    @retry
    def list_device(self):
        """
            Returns:
                SelectedGrids[AdbDeviceWithStatus]:
        """
        devices = []
        # try:
        with self.adb_client._connect() as c:
            """
                好像和 adb devices / adb get-serialno 差不多
                output: emulator-5554	device

                https://cs.android.com/android/platform/superproject/+/master:packages/modules/adb/SERVICES.TXT
            """
            c.send_command("host:devices")
            c.check_okay()
            output = c.read_string_block()
            for line in output.splitlines():
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue
                """
                    status: str = 'device'
                """
                device = AdbDeviceWithStatus(self.adb_client, parts[0], parts[1])
                devices.append(device)

        # except ConnectionResetError as e:
        #     # Happens only on CN users.
        #     # ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。
        #     logger.error(e)
        #     if '强迫关闭' in str(e):
        #         logger.critical('无法连接至ADB服务，请关闭UU加速器、原神私服、以及一些劣质代理软件。')

        return SelectedGrids(devices)

    def adb_shell(self, cmd, stream=False, recvall=True, timeout=10, rstrip=True):
        """
        Equivalent to `adb -s <serial> shell <*cmd>`

        Args:
            cmd (list, str):
            stream (bool): Return stream instead of string output (Default: False)
            recvall (bool): Receive all data when stream=True (Default: True)
            timeout (int): (Default: 10)
            rstrip (bool): Strip the last empty line (Default: True)

        Returns:
            str if stream=False
            bytes if stream=True and recvall=True
            socket if stream=True and recvall=False
        """
        if not isinstance(cmd, str):
            cmd = list(map(str, cmd))
        if stream:
            result = self.adb.shell(cmd, stream=stream, timeout=timeout, rstrip=rstrip)
            if recvall:
                # bytes
                return recv_all(result)
            else:
                # socket
                return result
        else:
            result = self.adb.shell(cmd, stream=stream, timeout=timeout, rstrip=rstrip)
            result = remove_shell_warning(result)
            # str
            return result

    @staticmethod
    def sleep(second):
        """
        Args:
            second(int, float, tuple):
        """
        time.sleep(ensure_time(second))
