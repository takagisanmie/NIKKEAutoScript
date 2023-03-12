import time


def getTaskResetTime():
    # 当天凌晨
    midnight = time.mktime(time.localtime(int(time.time() - int(time.time() - time.timezone) % 86400)))
    # 现在
    now = time.time()
    # 当天凌晨+4小时 < 现在 重置为下一天
    if midnight + 14400 < now:
        return round(midnight + 100800)
    # 当天凌晨+4小时 > 现在 重置为当天凌晨4点
    else:
        return round(midnight + 14400)


def after(second):
    # 现在
    now = time.time()
    return round(second + now)


def getStrfTime(_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_time))


class Timer:
    def __init__(self, limit, count=0):
        """
        Args:
            limit (int, float): Timer limit
            count (int): Timer reach confirm count. Default to 0.
                When using a structure like this, must set a count.
                Otherwise it goes wrong, if screenshot time cost greater than limit.

                if self.appear(MAIN_CHECK):
                    if confirm_timer.reached():
                        pass
                else:
                    confirm_timer.reset()

                Also, It's a good idea to set `count`, to make alas run more stable on slow computers.
                Expected speed is 0.35 second / screenshot.
        """
        self.limit = limit
        self.count = count
        self._current = 0
        self._reach_count = count

    def start(self):
        if not self.started():
            self._current = time.time()
            self._reach_count = 0

        return self

    def started(self):
        return bool(self._current)

    def current(self):
        """
        Returns:
            float
        """
        if self.started():
            return time.time() - self._current
        else:
            return 0.

    def reached(self):
        """
        Returns:
            bool
        """
        self._reach_count += 1
        # print(f'当前时间:{round(time.time(), 2)}', f'完成时间:{round(self._current, 2)}', f'限制时间:{self.limit}',
        #       f'抵达次数:{self._reach_count}',
        #       f'总次数:{self.count}')

        # print(time.time() - self._current > self.limit, self._reach_count > self.count)
        return time.time() - self._current > self.limit and self._reach_count > self.count

    def reset(self):
        self._current = time.time()
        self._reach_count = 0
        return self

    def clear(self):
        self._current = 0
        self._reach_count = self.count
        return self

    def reached_and_reset(self):
        """
        Returns:
            bool:
        """
        if self.reached():
            self.reset()
            return True
        else:
            return False

    def wait(self):
        """
        Wait until timer reached.
        """
        diff = self._current + self.limit - time.time()
        if diff > 0:
            time.sleep(diff)

    def __str__(self):
        return f'Timer(limit={round(self.current(), 3)}/{self.limit}, count={self._reach_count}/{self.count})'

    __repr__ = __str__


class TimeoutException(Exception):
    pass


def func():
    # do some operation that may take too long time
    time.sleep(2)
    print('fun')


if __name__ == '__main__':

    timer = Timer(1).start()  # set limit to 3 seconds

    func()

    if timer.reached():
        print(1)
    else:
        print(2)

    # # Example usage
    # timeout = 5.0  # wait for user input for up to 5 seconds
    # timer = Timer(timeout).start()
    #
    # print(f'Please enter something within {timeout} seconds...')
    #
    # while not timer.reached():
    #     user_input = input('> ')
    #
    #     if user_input:
    #         print(f'You entered: {user_input}')
    #         break
    #
    #     time.sleep(0.1)
    #
    # if timer.reached():
    #     print(f'Timeout: {timeout} seconds elapsed without any input.')
    # else:
    #     print(f'Successfully input within {timeout} seconds.')
