from common.exception import Timeout
from module.tools.timer import Timer
from module.ui.page import *
from common.enum.enum import *
from module.tools.match import match
from module.base.base import BaseModule


class UI(BaseModule):
    current_page: Page = None

    def where(self, skip_first_screenshot=True):

        timeout = Timer(180).start()
        click_timer = Timer(1.2)
        confirm_timer = Timer(1, count=5).start()

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
                if not hasattr(self.device, "image") or self.device.image is None:
                    self.device.screenshot()
            else:
                self.device.screenshot()

            # 匹配主页面标识
            for page in page_list:
                for sign in page.signs:
                    if match(img=self.device.image, template=sign, _result=ImgResult.SIMILARITY) is not None:
                        UI.current_page = page
                        if click_timer.reached():
                            return page
                    else:
                        continue

            # 匹配子页面标识
            result = self.checkChildPage()
            if result is not None:
                UI.current_page = result
                # self.closeChildPage()
                if click_timer.reached():
                    return result

            # 在未知页面,但是有主页面按钮
            if click_timer.reached() and self.device.appear_then_click(home, screenshot=True):
                click_timer.reset()
                timeout.reset()
                self.device.sleep(5)
                continue

            # 礼包
            if click_timer.reached() and self.device.appear(gift) and self.device.appear_then_click(confirm):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(reward):
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.clickTextLocation('领取奖励'):
                timeout.reset()
                click_timer.reset()
                confirm_timer.reset()
                continue

            # 月卡
            if click_timer.reached() and self.device.textStrategy('补给品每日奖励', None, OcrResult.TEXT):
                self.device.multiClickLocation((360, 850))
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.appear_then_click(gift):
                timeout.reset()
                click_timer.reset()
                continue

            if self.device.appear(system_error) or self.device.appear(download_sign):
                UI.current_page = page_login
                from module.handler.login import LoginHandler
                LoginHandler(self.config, device=self.device, socket=self.socket).handle_app_login(where=False)
                timeout.reset()
                click_timer.reset()
                continue

            if self.device.textStrategy('根据累积登入天数', None, OcrResult.TEXT):
                self.device.multiClickLocation((20, 600))
                self.device.sleep(5)
                timeout.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.device.textStrategy('剩余时间', None, OcrResult.TEXT):
                self.device.multiClickLocation((20, 600))
                self.device.sleep(5)
                timeout.reset()
                click_timer.reset()
                continue

            if timeout.reached():
                raise Timeout

            self.WARNING('unknown page')

    def go(self, destination, skip_first_screenshot=True):
        self.INFO(f'go to: {destination.name}')
        print(f'go to: {destination.name}')
        self.where(skip_first_screenshot=skip_first_screenshot)
        if UI.current_page == destination:
            return

        if self.isChildPage(UI.current_page):
            self.closeChildPage()

        if self.isChildPage(destination):
            path = []
            self.go_to_child_page(destination, path, destination)
            self.go_to_destination(path)
            return

        if destination is page_main:
            self.go_to_main()
            return

        # path1 = []
        # self.getPathByBack(path1, UI.current_page)
        # path2 = []
        # self.getPathByParent(path2, destination)
        # for a_index, a_value in enumerate(path1):
        #     for b_index, b_value in enumerate(path2):
        #         if a_value['destination'].name == b_value['destination'].name:
        #             path1 = path1[b_index:a_index + 1]
        #             path2 = path2[b_index + 1:len(path2)]
        #
        # path = path1 + path2
        #
        # for index, value in enumerate(path):
        #     if value['destination'] is page_main:
        #         path = path[index + 1:len(path)]
        #         self.go_to_main()

        path1 = []
        self.getPathByBack(path1, UI.current_page)
        path2 = []
        self.getPathByParent(path2, destination)

        flag = False
        for i1, value1 in enumerate(path1):
            _destination1 = \
                list(filter(lambda x: x[1]['id'] == value1['button']['id'], path1[i1]['page'].links.items()))[0][0].name

            for i2, value2 in enumerate(path2):
                _destination2 = \
                    list(filter(lambda x: x[1]['id'] == value2['button']['id'], path2[i2]['page'].links.items()))[0][
                        0].name

                if _destination1 == _destination2:
                    path1 = path1[:i1 + 1]
                    path2 = path2[i2 + 1:]
                    flag = True
                    break

            if flag:
                break

        path = path1 + path2

        for index, value in enumerate(path):
            if value['destination'] is page_main:
                path = path[index + 1:]
                key = list(filter(lambda k: k is page_main, UI.current_page.links.keys()))
                if key:
                    path.insert(0, self.getPath(value['page'], page_main, UI.current_page.links[key[0]]))

            if value['page'] is UI.current_page and value['destination'] is destination:
                path = path[index:]

        self.go_to_destination(path)

    def getPathByParent(self, array, page):
        if page is page_main:
            return

        if page.parent is not None:
            if page in page.parent.links.keys():
                path = self.getPath(page.parent, page, page.parent.links[page])  # Page == Button
                array.insert(0, path)
            self.getPathByParent(array, page.parent)

    def getPathByBack(self, array, page):
        if page is page_main:
            return

        for k, v in page.links.items():
            # if v is back and k:
            if v is back and k:
                path = self.getPath(page, k, v)
                array.append(path)
                self.getPathByBack(array, k)

            # page_nikke_list 没有 back，home
            elif page is page_nikke_list and v is to_main and k:
                path = self.getPath(page, k, v)
                array.append(path)
                self.getPathByBack(array, k)

        return array

    def getPath(self, page, destination, button):
        path = {
            'page': page,
            'destination': destination,
            'button': button,
        }
        return path

    def go_to_main(self):

        timeout = Timer(20).start()
        confirm_timer = Timer(1, count=1).start()
        click_timer = Timer(1.2)

        while 1:

            self.device.screenshot()

            if self.device.appear(main_sign):
                return

            for k, v in UI.current_page.links.items():
                if k is page_main:
                    if click_timer.reached() and self.device.appear_then_click(v):
                        timeout.reset()
                        confirm_timer.reset()
                        click_timer.reset()
                        break

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def isChildPage(self, page):
        if page in page_list:
            return False
        else:
            return True

    def checkChildPage(self):
        for parent_page in page_list:
            result = self.checkAllChildPage(parent_page)
            if result is not None:
                return result

    def checkAllChildPage(self, page):
        for child_page in page.children_links:
            for child_sign in child_page.signs:
                sl = match(img=self.device.image, template=child_sign, _result=ImgResult.SIMILARITY)
                if sl is not None and sl > 0.8:
                    return child_page

            if (len(child_page.children_links)) > 0:
                result = self.checkAllChildPage(child_page)
                if result is not None:
                    return result

    def closeChildPage(self):
        timeout = Timer(20).start()
        while 1:
            self.device.screenshot()
            if self.device.appear_then_click(UI.current_page.closeButton):
                timeout.reset()
                continue

            if self.device.appear(UI.current_page.parent.signs[0]) and self.device.hide(UI.current_page.closeButton):
                break

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

        UI.current_page = UI.current_page.parent
        if self.isChildPage(UI.current_page):
            self.closeChildPage()

    def go_to_child_page(self, page, array=None, destination=None):
        #   main_page    main_page         child_page
        # page_mian => page_outpost => page_commission
        # if page.parent is not None and page.parent in page_list and page.parent is page_main:
        if page.parent is not None and page.parent in page_list and page is not destination:
            self.go(page)
            return page
        elif page.parent is not None:
            if page in page.parent.children_links.keys():
                path = self.getPath(page.parent, page, page.parent.children_links[page])
                array.insert(0, path)
            return self.go_to_child_page(page.parent, array, destination)
        else:
            self.go(page)
            return page

    def go_to_destination(self, path):

        timeout = Timer(30).start()
        confirm_timer = Timer(limit=0, count=len(path)).start()
        click_timer = Timer(1.2)

        while 1:
            for index, value in enumerate(path):
                self.device.screenshot()

                for i in value['destination'].signs:
                    if self.device.appear(i):
                        path = path[index + 1:]
                        confirm_timer.count = len(path)
                        if confirm_timer.reached():
                            return
                        break

                if click_timer.reached() and self.device.appear_then_click(value['button']):
                    click_timer.reset()
                    timeout.reset()
                    click_timer.wait()
                    confirm_timer.reset()
                    click_timer.reset()

            if timeout.reached():
                self.ERROR('wait too long')
                raise Timeout

    def stop_until_reset_time(self):
        import time

        midnight = time.mktime(time.localtime(int(time.time() - int(time.time() - time.timezone) % 86400)))
        now = time.time()

        reset_time = round(midnight + 14400)
        reset_time2 = round(midnight + 14340)

        if reset_time > now >= reset_time2:
            server = int(self.config.get('Server', self.config.config_dict))

            package_name = None

            if server == NIKKEServer.JP and self.device.jp_package in self.device.u2.app_list():
                package_name = self.device.jp_package

            elif server == NIKKEServer.TW and self.device.tw_package in self.device.u2.app_list():
                package_name = self.device.tw_package

            if package_name in self.device.u2.app_list_running():
                self.device.u2.app_stop(package_name)
                self.INFO('停止NIKKE，直到4:00AM')
                self.device.sleep(40)
