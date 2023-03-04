import assets


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


# 主页面
page_main = Page(signs=[assets.in_menu_sign, assets.in_menu_sign2], name='page_main')

# 主页面-子页面
# 主页面-奖励箱页
page_main_child_reward_box = ChildPage(signs=[assets.in_menu_reward_box_sign], parent=page_main,
                                       name='page_main_child_reward_box', closeButton=assets.close)
# 主页面-奖励箱页-一键歼灭页
page_main_child_reward_box_child_destroy = ChildPage(signs=[assets.in_menu_reward_box_destroy_close],
                                                     parent=page_main_child_reward_box,
                                                     name='page_main_child_reward_box_child_destroy',
                                                     closeButton=assets.in_menu_reward_box_destroy_close)

# 主页面-奖励箱页-链接
page_main_child_reward_box.link_chlid(button=assets.in_menu_reward_to_destroy,
                                      destination=page_main_child_reward_box_child_destroy)

# 主页面-好友页
page_main_child_friends = ChildPage(signs=[assets.in_friends_sign], parent=page_main,
                                    name='page_main_child_friends', closeButton=assets.close2)

# 主页面-公告页
page_main_child_announcement = ChildPage(signs=[assets.in_menu_announcement_sign], parent=page_main,
                                         name='page_main_child_announcement', closeButton=assets.close6)

# 主页面-登录奖励
page_main_child_event_login = ChildPage(signs=[assets.in_event_login_sign], parent=page_main,
                                        name='page_main_child_event_login', closeButton=assets.in_event_login_close)

# 主页面-子页面链接
page_main.link_chlid(button=assets.in_menu_to_reward_box, destination=page_main_child_reward_box)
page_main.link_chlid(button=assets.in_menu_to_friends, destination=page_main_child_friends)
page_main.link_chlid(button=None, destination=page_main_child_announcement)

# Nikke菜单页
page_Nikke_menu = Page(signs=[assets.in_nikke_list_sign], name='page_Nikke_menu', parent=page_main)
page_Nikke_menu.link(button=assets.home, destination=page_main)
page_Nikke_menu.link(button=assets.back, destination=page_main)

# 主页面- Nikke菜单页链接
page_main.link(button=assets.in_menu_to_nikke_list, destination=page_Nikke_menu)

# Nikke好感度页
page_conversation_list = Page(signs=[assets.in_conversation_list_sign], name='page_conversation_list',
                              parent=page_Nikke_menu)
page_conversation_list.link(button=assets.back, destination=page_Nikke_menu)
page_conversation_list.link(button=assets.home, destination=page_main)

# Nikke菜单页链接-Nikke好感度页
page_Nikke_menu.link(button=assets.in_nikke_list_to_conversation_list, destination=page_conversation_list)

# Nikke个人好感度页
page_Nikke_friendship = Page(signs=[assets.in_conversation_detail_sign], name='page_Nikke_friendship',
                             parent=page_conversation_list)
page_Nikke_friendship.link(button=assets.back, destination=page_conversation_list)
page_Nikke_friendship.link(button=assets.home, destination=page_main)

# 方舟页
page_ark = Page(signs=[assets.in_ark_sign], name='page_ark', parent=page_main)
page_ark.link(button=assets.home, destination=page_main)
page_ark.link(button=assets.back, destination=page_main)

# 主页面-方舟页链接
page_main.link(button=assets.in_menu_to_ark, destination=page_ark)

# 商店页
page_free_store = Page(signs=[assets.in_free_store_sign], name='page_free_store', parent=page_main)
page_free_store.link(button=assets.home, destination=page_main)
page_free_store.link(button=assets.back, destination=page_main)

# 主页面-商店页
page_main.link(button=assets.in_menu_to_free_store, destination=page_free_store)

# 前哨基地页
page_outpost = Page(signs=[assets.in_outpost_sign], name='page_outpost', parent=page_main)
page_outpost.link(button=assets.home, destination=page_main)
page_outpost.link(button=assets.back, destination=page_main)

# 主页面-前哨基地页
page_main.link(button=assets.in_menu_to_outpost, destination=page_outpost)

# 前哨基地页-公告栏
page_outpost_child_commission = ChildPage(signs=[assets.in_outpost_commission_sign],
                                          name='page_outpost_child_commission', parent=page_outpost,
                                          closeButton=assets.close3)

# 前哨基地页-公告栏链接
page_outpost.link_chlid(button=assets.in_outpost_to_commission, destination=page_outpost_child_commission)

# 竞技场入口面
page_arean_gate = Page(signs=[assets.in_arena_sign], name='page_arean_gate', parent=page_ark)
page_arean_gate.link(button=assets.back, destination=page_ark)
page_arean_gate.link(button=assets.home, destination=page_main)

# 方舟页-竞技场入口面
page_ark.link(button=assets.in_ark_to_arean_gate, destination=page_arean_gate)

# 新人竞技场页
page_arean_Rookie = Page(signs=[assets.in_arena_Rookie_sign], name='page_arean_Rookie', parent=page_arean_gate)
page_arean_Rookie.link(button=assets.back, destination=page_arean_gate)
page_arean_Rookie.link(button=assets.home, destination=page_main)

# 竞技场入口面-新人竞技场页
page_arean_gate.link(button=assets.in_arena_gate_to_Rookie, destination=page_arean_Rookie)

# 模拟室页
page_simulation_room = Page(signs=[assets.in_simulation_room_sign], name='page_simulation_room', parent=page_ark)
page_simulation_room.link(button=assets.back, destination=page_ark)
page_simulation_room.link(button=assets.home, destination=page_main)

# 方舟页-模拟室页
page_ark.link(button=assets.in_ark_to_arean_simulation_room, destination=page_simulation_room)

# 模拟室页-开始页
page_simulationOption_room = ChildPage(signs=[assets.in_simulationOption_sign], parent=page_simulation_room,
                                       name='page_simulationOption_room', closeButton=assets.close4)

page_simulation_room.link_chlid(button=assets.in_simulation_to_option, destination=page_simulationOption_room)

# 模拟室事件选项页
page_simulation_room2 = Page(signs=[assets.in_Simulation_BUFF], name='page_simulation_room2', parent=None)

# 登录页
page_login = Page(signs=[assets.login_sign], name='page_login')
page_login_child_announcement = ChildPage(signs=[assets.login_announcement_sign], parent=page_login,
                                          name='page_login_child_announcement', closeButton=assets.close5)

page_login.link_chlid(button=None, destination=page_login_child_announcement)

# 奖励页
page_rewards = Page(signs=[assets.rewards_page], name='page_rewards')

page_list = [page_main, page_rewards, page_login, page_Nikke_menu, page_conversation_list, page_Nikke_friendship,
             page_ark, page_free_store, page_outpost,
             page_simulation_room, page_arean_gate,
             page_arean_Rookie, page_simulation_room2]
