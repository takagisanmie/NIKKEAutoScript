import json
from datetime import datetime

import requests

from module.logger import logger
from module.ui.ui import UI


class NoCookie(Exception):
    pass


class LIPass(UI):
    def run(self):
        url = "https://pass.levelinfinite.com/api/rewards/proxy/lipass/Points/DailyCheckIn"
        local_now = datetime.now()
        _ = local_now.replace(hour=8, minute=0, second=0, microsecond=0)
        if local_now > _:
            try:
                # 请勿泄露自己的Cookie
                lip_user_name = ""
                lip_uid = ""
                lip_token = ""
                if lip_token.strip() == "":
                    raise NoCookie
                lip_openid = ""
                lip_expire_time = ""
                lip_picture_url = ""
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                    "Cookie": f"lip_user_name={lip_user_name};"
                              f"lip_uid={lip_uid};"
                              "lip_channelid=131;"
                              f"lip_token={lip_token}; "
                              f"lip_openid={lip_openid};"
                              f"lip_adult_status=1;"
                              f"lip_expire_time={lip_expire_time}; "
                              f"lip_picture_url={lip_picture_url}"
                }
                data = '{"task_id":"15"}'
                res = requests.post(url=url, data=data, headers=headers, verify=False)
                msg = json.loads(res.text)
                if msg['msg'] == 'ok':
                    logger.info('check in success')
                if msg['msg'] == 'system error':
                    logger.warn('perhaps have already been checked in')
                res.close()
            except NoCookie as e:
                logger.error("NoCookie")
                logger.warn(
                    "if you want to check in at lipass, please confirm that your Cookie in NKAS\module\lipass\lipass.py is correct.")
            except Exception as e:
                logger.error(e)
            self.config.task_delay(server_update=True)
        else:
            self.config.task_delay(minute=60)
