import argparse
import subprocess
from functools import cached_property
import requests

from module.device.method.uiautomator_2 import Uiautomator2

adb = ['adb']
# package = 'com.torther.droidcasts'
package = 'com.rayworks.droidcast'

parser = argparse.ArgumentParser(
    description='Automation script to activate capturing screenshot of Android device')
parser.add_argument('-s', '--serial', dest='device_serial',
                    help='Device serial number (adb -s option)')
parser.add_argument(
    '-p',
    '--port',
    dest='port',
    nargs='?',
    const=53516,
    type=int,
    default=53516,
    help='Port number to be connected, by default it\'s 53516')
args_in = parser.parse_args()


class DroidCast(Uiautomator2):
    _droidcast_port: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._droidcast_port = '53516'

    def screenshot(self):
        import cv2
        import numpy as np
        self.sleep(0.1)
        image = self.droidcast_session.get(self.droidcast_url(), timeout=3).content
        image = np.frombuffer(image, np.uint8)
        self.image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return self.image

    @cached_property
    def droidcast_session(self):
        from module.thread.thread import futures
        self.installDroidCast()
        futures.run_droidcast(self.initDroidCast)
        session = requests.Session()
        self.sleep(5)
        return session

    def stop_droidcast(self):
        import threading
        from module.thread.thread import threadManager
        from module.base.decorator import del_cached_property

        for thread in threading.enumerate():
            if 'Droidcast' in thread.name:
                threadManager.stopThread(thread)
                continue

        del_cached_property(self, 'droidcast_session')

    def droidcast_url(self, url='/screenshot'):
        return f'http://127.0.0.1:{self._droidcast_port}{url}'

    def installDroidCast(self):
        if package not in self.u2.app_list():
            self.u2.app_install(self.config.Droid_Cast_APK_Path)
            self.sleep(8)

    def initDroidCast(self):
        try:
            class_path = self.locate_apk_path()
            (code, _, err) = self.run_adb(
                ["forward", "tcp:%d" % args_in.port, "tcp:%d" % args_in.port])
            # print(">>> adb forward tcp:%d " % args_in.port, code)
            args = ["shell",
                    class_path,
                    "app_process",
                    "/",  # unused
                    package + '.Main',
                    "--port=%d" % args_in.port]

            self.run_adb(args, pipeOutput=False)

        except (Exception) as e:
            print(e)

    def run_adb(self, args, pipeOutput=True):
        args_in.device_serial = self.config.Simulator_Serial
        if args_in.device_serial:
            args = adb + ['-s', args_in.device_serial] + args
        else:
            args = adb + args

        # print('exec cmd : %s' % args)
        out = None
        if (pipeOutput):
            out = subprocess.PIPE

        p = subprocess.Popen([str(arg)
                              for arg in args], stdout=out, encoding='utf-8')
        stdout, stderr = p.communicate()
        return (p.returncode, stdout, stderr)

    def locate_apk_path(self):
        (rc, out, _) = self.run_adb(["shell", "pm",
                                     "path",
                                     package])
        if rc or out == "":
            raise RuntimeError(
                "Locating apk failure, have you installed the app successfully?")

        prefix = "package:"
        postfix = ".apk"
        beg = out.index(prefix, 0)
        end = out.rfind(postfix)

        return "CLASSPATH=" + out[beg + len(prefix):(end + len(postfix))].strip()
