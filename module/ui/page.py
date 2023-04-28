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

# Destroy
page_destroy = Page(DESTROY_CHECK)
page_destroy.link(button=DESTROY_GOTO_REWARD, destination=page_reward)
page_reward.link(button=REWARD_GOTO_DESTROY, destination=page_destroy)

# friend
page_friend = Page(FRIEND_CHECK)
page_friend.link(button=FRIEND_GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_FRIEND, destination=page_friend)

# team
page_team = Page(TEAM_CHECK)
page_team.link(button=TEAM_GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_TEAM, destination=page_team)

# conversation
page_conversation = Page(CONVERSATION_CHECK)
page_conversation.link(button=GOTO_BACK, destination=page_team)
page_conversation.link(button=GOTO_MAIN, destination=page_main)
page_team.link(button=TEAM_GOTO_CONVERSATION, destination=page_conversation)

# ark
page_ark = Page(ARK_CHECK)
page_ark.link(button=GOTO_BACK, destination=page_main)
# page_ark.link(button=GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_ARK, destination=page_ark)

# simulation_room
page_simulation_room = Page(SIMULATION_ROOM_CHECK)
page_simulation_room.link(button=GOTO_BACK, destination=page_ark)
page_simulation_room.link(button=GOTO_MAIN, destination=page_main)
page_ark.link(button=ARK_GOTO_SIMULATION_ROOM, destination=page_simulation_room)

# arena
page_arena = Page(ARENA_CHECK)
page_arena.link(button=GOTO_BACK, destination=page_ark)
page_arena.link(button=GOTO_MAIN, destination=page_main)
page_ark.link(button=ARK_GOTO_ARENA, destination=page_arena)

# rookie arena
page_rookie_arena = Page(ROOKIE_ARENA_CHECK)
page_rookie_arena.link(button=GOTO_BACK, destination=page_arena)
page_rookie_arena.link(button=GOTO_MAIN, destination=page_main)
page_arena.link(button=ARENA_GOTO_ROOKIE_ARENA, destination=page_rookie_arena)

# special arena
page_special_arena = Page(SPECIAL_ARENA_CHECK)
page_special_arena.link(button=GOTO_BACK, destination=page_arena)
page_special_arena.link(button=GOTO_MAIN, destination=page_main)
page_arena.link(button=ARENA_GOTO_SPECIAL_ARENA, destination=page_special_arena)

# outpost
page_outpost = Page(OUTPOST_CHECK)
page_outpost.link(button=GOTO_BACK, destination=page_main)
# page_outpost.link(button=GOTO_MAIN, destination=page_main)
page_main.link(button=MAIN_GOTO_OUTPOST, destination=page_outpost)

# commission
page_commission = Page(COMMISSION_CHECK)
page_commission.link(button=COMMISSION_GOTO_OUTPOST, destination=page_outpost)
# page_outpost.link(button=GOTO_MAIN, destination=page_main)
page_outpost.link(button=OUTPOST_GOTO_COMMISSION, destination=page_commission)
