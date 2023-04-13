import traceback

from module.ui.assets import *


class Page:
    parent = None

    def __init__(self, check_button):
        self.check_button = check_button
        self.links = {}
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        self.name = text[:text.find('=')].strip()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def link(self, button, destination):
        self.links[destination] = button


# Main
page_main = Page(MAIN_CHECK)

# Unknown
page_unknown = Page(None)
page_unknown.link(button=GOTO_MAIN, destination=page_main)

# Reward
page_reward = Page(REWARD_CHECK)
page_reward.link(button=REWARD_GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_REWARD, destination=page_reward)

# friend
page_friend = Page(FRIEND_CHECK)
page_friend.link(button=FRIEND_GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_FRIEND, destination=page_friend)

# ark
page_ark = Page(ARK_CHECK)
page_ark.link(button=GOTO_BACK, destination=page_main)
# page_ark.link(button=GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_ARK, destination=page_ark)

# arena
page_arena = Page(ARENA_CHECK)
page_arena.link(button=GOTO_BACK, destination=page_ark)
page_arena.link(button=GOTO_MAIN, destination=page_main)
page_ark.link(button=ARK_GOTO_ARENA, destination=page_arena)

# special arena
page_special_arena = Page(SPECIAL_ARENA_CHECK)
page_special_arena.link(button=GOTO_BACK, destination=page_arena)
page_special_arena.link(button=GOTO_MAIN, destination=page_main)
page_arena.link(button=ARENA_GOTO_SPECIAL_ARENA, destination=page_special_arena)
