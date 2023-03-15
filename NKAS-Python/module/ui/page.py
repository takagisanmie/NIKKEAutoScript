from assets import *


class BasePage:
    def __init__(self, signs, parent=None, name=None, closeButton=None):
        self.signs = signs
        self.parent = parent
        self.links = {}
        self.children_links = {}
        self.name = name
        self.closeButton = closeButton

    def link(self, button, destination):
        self.links[destination] = button

    def link_chlid(self, button, destination):
        self.children_links[destination] = button


class Page(BasePage):
    pass


class ChildPage(BasePage):
    pass


class Button:
    def __init__(self, location, template, name=None):
        self.location = location
        self.template = template
        self.name = name


# 主页面
page_main = Page(signs=[main_sign], name='page_main')

# 方舟页
page_ark = Page(signs=[ark_sign], name='page_ark', parent=page_main)
page_ark.link(button=home, destination=page_main)
page_ark.link(button=back, destination=page_main)

page_main.link(button=to_ark, destination=page_ark)

# nikke列表
page_nikke_list = Page(signs=[nikke_list_sign], name='page_nikke_list', parent=page_main)
page_nikke_list.link(button=to_main, destination=page_main)

page_main.link(button=to_nikke_list, destination=page_nikke_list)

# 物品栏
page_inventory = Page(signs=[inventory_sign], name='page_inventory', parent=page_nikke_list)
page_inventory.link(button=to_nikke_list, destination=page_nikke_list)
page_inventory.link(button=to_main, destination=page_main)

page_nikke_list.link(button=to_inventory, destination=page_inventory)

# 咨询列表
page_conversation_list = Page(signs=[conversation_list_sign], name='page_conversation_list', parent=page_nikke_list)
page_conversation_list.link(button=home, destination=page_main)
page_conversation_list.link(button=back, destination=page_nikke_list)

page_nikke_list.link(button=to_conversation_list, destination=page_conversation_list)

# 解放
page_liberation = Page(signs=[liberation_sign], name='page_liberation', parent=page_nikke_list)
page_liberation.link(button=home, destination=page_main)
page_liberation.link(button=back, destination=page_nikke_list)

page_nikke_list.link(button=to_liberation, destination=page_liberation)

# 咨询详情
page_conversation_detail = Page(signs=[conversation_detail_sign], name='page_conversation_detail',
                                parent=page_conversation_list)
page_conversation_detail.link(button=home, destination=page_main)
page_conversation_detail.link(button=back, destination=page_conversation_list)

# 奖励箱
page_reward_box = ChildPage(signs=[reward_box_sign], parent=page_main,
                            name='page_reward_box', closeButton=reward_box_close)

page_main.link_chlid(button=to_reward_box, destination=page_reward_box)

# 每日任务
page_daily = ChildPage(signs=[daily_sign], parent=page_main,
                       name='page_daily', closeButton=daily_close)

page_main.link_chlid(button=to_daily, destination=page_daily)

# Pass
page_pass = ChildPage(signs=[pass_sign], parent=page_main,
                      name='page_pass', closeButton=pass_close)

page_main.link_chlid(button=to_pass, destination=page_pass)

# 好友
page_friends = ChildPage(signs=[friend_sign], parent=page_main,
                         name='page_friends', closeButton=friend_close)

page_main.link_chlid(button=to_friend, destination=page_friends)

# 邮件
page_mail = ChildPage(signs=[mail_sign], parent=page_main,
                      name='page_mail', closeButton=mail_close)

page_main.link_chlid(button=to_mail, destination=page_mail)

# 公告
page_notice = ChildPage(signs=[notice_sign], parent=page_main,
                        name='page_notice', closeButton=notice_close)

page_main.link_chlid(button=None, destination=page_notice)

# 歼灭
page_destroy = ChildPage(signs=[destroy_sign], parent=page_reward_box,
                         name='page_destroy', closeButton=destroy_close)

page_reward_box.link_chlid(button=to_destroy, destination=page_destroy)

# 商店
page_free_store = Page(signs=[free_store_sign], name='page_free_store', parent=page_main)
page_free_store.link(button=home, destination=page_main)
page_free_store.link(button=back, destination=page_main)

page_main.link(button=to_free_store, destination=page_free_store)

# 模拟室
page_simulation_room = Page(signs=[simulation_room_sign], name='page_simulation_room', parent=page_ark)
page_simulation_room.link(button=home, destination=page_main)
page_simulation_room.link(button=back, destination=page_ark)

page_ark.link(button=to_simulation_room, destination=page_simulation_room)

# 无限之塔
page_tribe_tower = Page(signs=[tribe_tower_sign], name='page_tribe_tower', parent=page_ark)
page_tribe_tower.link(button=home, destination=page_main)
page_tribe_tower.link(button=back, destination=page_ark)

page_ark.link(button=to_tower, destination=page_tribe_tower)

# 真无限塔
page_infinite_tower = Page(signs=[infinite_tower_sign], name='page_infinite_tower', parent=page_tribe_tower)
page_infinite_tower.link(button=home, destination=page_main)
page_infinite_tower.link(button=back, destination=page_tribe_tower)

page_tribe_tower.link(button=to_infinite_tower, destination=page_infinite_tower)

# 竞技场
page_arena = Page(signs=[arena_sign], name='page_arena', parent=page_ark)
page_arena.link(button=home, destination=page_main)
page_arena.link(button=back, destination=page_ark)

page_ark.link(button=to_arena, destination=page_arena)

# 新人竞技场
page_rookie_arena = Page(signs=[rookie_arena_sign], name='page_rookie_arena', parent=page_arena)
page_rookie_arena.link(button=home, destination=page_main)
page_rookie_arena.link(button=back, destination=page_arena)

page_arena.link(button=to_rookie_arena, destination=page_rookie_arena)

# 特殊竞技场
page_special_arena = Page(signs=[special_arena_sign], name='page_special_arena', parent=page_arena)
page_special_arena.link(button=home, destination=page_main)
page_special_arena.link(button=back, destination=page_arena)

page_arena.link(button=to_special_arena, destination=page_special_arena)

# 模拟室-选项
page_simulation_option = ChildPage(signs=[simulation_option_sign], parent=page_simulation_room,
                                   name='page_simulation_option', closeButton=simulation_option_close)

page_simulation_room.link_chlid(button=to_simulation_option, destination=page_simulation_option)

page_simulation = Page(signs=[simulation_sign], parent=page_ark,
                       name='page_simulation')
page_simulation.link(button=home, destination=page_main)
page_simulation.link(button=back, destination=page_ark)

# 前哨基地
page_outpost = Page(signs=[outpost_sign], name='page_outpost', parent=page_main)
page_outpost.link(button=home, destination=page_main)
page_outpost.link(button=back, destination=page_main)

page_main.link(button=to_outpost, destination=page_outpost)

from module.task.commission.commission_assets import commission_close

# 委托
page_outpost_commission = ChildPage(signs=[outpost_commission_sign], parent=page_outpost,
                                    name='page_outpost_commission', closeButton=commission_close)

page_outpost.link_chlid(button=to_commission, destination=page_outpost_commission)

# 登录
page_login = Page(signs=[login_sign], name='page_login')

page_list = [page_main, page_ark, page_nikke_list, page_inventory, page_liberation, page_conversation_list,
             page_conversation_detail,
             page_free_store,
             page_simulation_room, page_tribe_tower, page_infinite_tower, page_arena, page_rookie_arena,
             page_special_arena, page_outpost,
             page_simulation, page_login]
