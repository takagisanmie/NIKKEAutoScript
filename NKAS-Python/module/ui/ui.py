from functools import cached_property

import assets
from module.ui.page import *
from common.enum.enum import *
from module.base.decorator import run_once
from module.tools.match import match
from module.base.base import BaseModule


class UI(BaseModule):
    current_page: Page = None

    # @run_once
    def where(self, skip_first_screenshot=True):
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
                        return page
                    else:
                        continue

            # 匹配子页面标识
            result = self.checkChildPage()
            if result is not None:
                UI.current_page = result
                self.closeChildPage()

            # 在未知页面,但是有主页面按钮
            if self.device.isVisible(assets.home):
                self.device.click(assets.home, AssetResponse.ASSET_HIDE)
                continue

    def go(self, destination, skip_first_screenshot=True):
        self.INFO(f'go to: {destination.name}')
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

        path1 = []
        self.getPathByBack(path1, UI.current_page)
        path2 = []
        self.getPathByParent(path2, destination)
        for a_index, a_value in enumerate(path1):
            for b_index, b_value in enumerate(path2):
                if a_value['destination'].name == b_value['destination'].name:
                    path1 = path1[b_index:a_index + 1]
                    path2 = path2[b_index + 1:len(path2)]

        path = path1 + path2

        for index, value in enumerate(path):
            if value['destination'] is page_main:
                path = path[index + 1:len(path)]
                self.go_to_main()

        self.go_to_destination(path)

    def getPathByParent(self, array, page):
        if page is page_main:
            return

        if page.parent is not None:
            if page in page.parent.links.keys():
                path = self.getPath(page.parent.name, page, page.parent.links[page])  # Page == Button
                array.insert(0, path)
            self.getPathByParent(array, page.parent)

    def getPathByBack(self, array, page):
        if page is page_main:
            return

        for k, v in page.links.items():
            if v is assets.back and k:
                path = self.getPath(page.name, k, v)
                array.append(path)
                self.getPathByBack(array, k)

        return array

    def getPath(self, page, destination, button):
        path = {
            'page': page,
            'destination': destination,
            'button': button
        }
        return path

    def go_to_main(self):
        for k, v in UI.current_page.links.items():
            if k is page_main:
                self.device.click(v, AssetResponse.ASSET_SHOW, assets.in_menu_sign)
        pass

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
                if sl is not None and sl > 0.84:
                    return child_page

            if (len(child_page.children_links)) > 0:
                result = self.checkAllChildPage(child_page)
                if result is not None:
                    return result

    def closeChildPage(self):
        self.device.click(UI.current_page.closeButton, AssetResponse.ASSET_SHOW, UI.current_page.parent.signs[0])
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
                path = self.getPath(page.parent.name, page, page.parent.children_links[page])
                array.insert(0, path)
            return self.go_to_child_page(page.parent, array, destination)
        else:
            self.go(page)
            return page

    def go_to_destination(self, path):
        for index, value in enumerate(path):
            if index != len(path) - 1:
                next = path.__getitem__(index + 1)
                self.device.click(value['button'], AssetResponse.ASSET_SHOW, next['button'])
            else:
                self.device.click(value['button'], AssetResponse.ASSET_SHOW, value['destination'].signs[0])
