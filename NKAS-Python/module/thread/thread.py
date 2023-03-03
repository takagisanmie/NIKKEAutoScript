import threading
import inspect
import ctypes
import concurrent.futures


class ThreadManager:

    def getThread(self, target, func_name, name, args):
        func = getattr(target, func_name)
        new_thread = threading.Thread(target=func, name=name, args=args)
        return new_thread

    def asyncRaise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""

        tid = ctypes.c_long(tid)

        if not inspect.isclass(exctype):
            exctype = type(exctype)

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

        if res == 0:

            raise ValueError("invalid thread id")

        elif res != 1:

            # """if it returns a number greater than one, you're in trouble,

            # and you should call it again with exc=NULL to revert the effect"""

            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stopThread(self, thread):
        self.asyncRaise(thread.ident, SystemExit)


threadManager = ThreadManager()


class Futures:
    def __init__(self):
        self.queues = []

    def insertQueue(self, *args, **kwargs):
        self.queues.append(*args, **kwargs)
        pass

    def getExecutor(self, prefix='NKAS'):
        return concurrent.futures.ThreadPoolExecutor(thread_name_prefix=prefix)

    def as_completed(self):
        for future in concurrent.futures.as_completed(self.queues):  # 并发执行
            return future.result()

    def run(self, *args, **kwargs):
        executor = futures.getExecutor()
        futures.insertQueue(executor.submit(*args, **kwargs))
        return futures.as_completed()

    def submit(self, *args, **kwargs):
        executor = futures.getExecutor()
        futures.insertQueue(executor.submit(*args, **kwargs))


futures = Futures()
