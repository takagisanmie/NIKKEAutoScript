import functools
import time

# def Timeout(origin):
#     @functools.wraps(origin)
#     def prefix(*args, **kwargs):
#         timeout = Timer(20).start()
#         confirm_timer = Timer(0.5, count=3).start()
#         click_timer = Timer(0.3).reset()
#         res = None
#         while 1:
#             if click_timer.reached():
#                 res = origin(*args, **kwargs)
#                 click_timer.reset()
#                 confirm_timer.reset()
#
#             if confirm_timer.reached() and res:
#                 return res
#
#             if timeout.reached():
#                 return res
#
#     return prefix


