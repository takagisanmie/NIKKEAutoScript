from module.base.timer import Timer
from module.base.utils import mask_area
from module.redeem_codes.assets import *
from module.logger import logger
from module.ui.ui import UI
from module.redeem_codes.Nikke_scraping import *
import subprocess
from time import sleep


class RedeemCodes(UI):
    def redeem(self, skip_first_screenshot=True):
        logger.hr('Redeeming codes', 2)
        confirm_timer = Timer(7, count=2).start()
        click_timer = Timer(0.3)
        code_scrape = GetCodes()
        codes = code_scrape.get_codes()
        file = f"files/redeemed_codes_NIKKE.txt"

        codes_filtered = code_scrape._check_codes(codes)
        for code in codes_filtered:
            redeem_code_wrote = False


            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.device.screenshot()
                    self.device.image = mask_area(self.device.image, NOTICE_BUTTON.button)

                if confirm_timer.reached() and self.appear_then_click(NOTICE_BUTTON, offset=(5, 5), interval=6,
                                                                    threshold=0.8, static=False):
                    sleep(3)
                    self.ensure_sroll((360, 920), (360, 620), count=2, delay=0.6)
                    confirm_timer.reset()
                    click_timer.reset()
                    continue
                
                # if confirm_timer.reached() and self.appear(NOTICE_OPEN, offset=(5, 5), interval=1,
                #                                                     static=False, threshold=0.8):
                    
                #     confirm_timer.reset()
                #     click_timer.reset()
                #     continue
                if self.appear_then_click(FIND_CDKEY, offset=(10, 10), threshold=0.8) and confirm_timer.reached():
                    confirm_timer.reset()
                    click_timer.reset()
                    continue
                
                if self.appear_then_click(GO_TO_REDEEM, offset=(10, 10), threshold=0.8) and confirm_timer.reached():
                    confirm_timer.reset()
                    click_timer.reset()
                    continue
                
                if self.appear_text_then_click("输入CDKey") and confirm_timer.reached():
                    confirm_timer.reset()
                    click_timer.reset()
                    subprocess.run(["toolkit\\android-platform-tools\\adb.exe", "shell", "input", "text", f"{code}"])
                    redeem_code_wrote = True
                  
                    confirm_timer.reset()
                    click_timer.reset()
                            
                    if self.appear_text_then_click("立即兑换") and confirm_timer.reached() and redeem_code_wrote:
                        subprocess.run(["toolkit\\android-platform-tools\\adb.exe", "shell", "input", "keyevent", "100"])
                        click_timer.reset()
                        confirm_timer.reset()
                        redeem_code_wrote = False
                

                if self.appear_text_then_click("确定"):
                    subprocess.run(["toolkit\\android-platform-tools\\adb.exe", "shell", "input", "keyevent", "100"])
                    with open(file, "a") as f:
                        f.write(f"{code}\n")  
                    break
                sleep(1)


        # Function to press the back button using ADB
    def press_back_button(self):
        subprocess.run(["toolkit\\android-platform-tools\\adb.exe", "shell", "input", "keyevent", "KEYCODE_BACK"])

    def ensureUI(self):
        self.press_back_button()
        sleep(1)
        self.press_back_button()
        sleep(1)

    def run(self):
        self.redeem()
        self.ensureUI()
        self.config.task_delay(minute=120)
    
