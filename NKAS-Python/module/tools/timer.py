import time
import datetime


def getNextTuesday():
    today = datetime.date.today()
    days = (1 - today.weekday()) % 7
    days = 7 if not days else days
    next_tuesday = today + datetime.timedelta(days=days)
    date_obj = datetime.datetime.strptime(str(next_tuesday), "%Y-%m-%d")
    return [str(next_tuesday), int(date_obj.timestamp())]


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


if __name__ == '__main__':
    midnight = time.mktime(time.localtime(int(time.time() - int(time.time() - time.timezone) % 86400)))
    # 现在
    now = time.time()
    reset_time = round(midnight + 14400)
    reset_time2 = round(midnight + 14340)
    if reset_time > now >= reset_time2:
        print(111)


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
