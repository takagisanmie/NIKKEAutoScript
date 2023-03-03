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


def getStrfTime(_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_time))
