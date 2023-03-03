from module.ui.page import Page, ChildPage


class EventAssets:
    part1_normal_A: dict = None
    part1_normal_B: dict = None
    part1_normal: dict = None
    part1_normal_locked: dict = None
    part1_normal_finished: dict = None

    part1_hard_A: dict = None
    part1_hard_B: dict = None
    part1_hard: dict = None
    part1_hard_locked: dict = None
    part1_hard_finished: dict = None

    # 小活动才有
    part1_difficulty_normal: dict = None
    part1_difficulty_hard: dict = None

    part2_normal_A: dict = None
    part2_normal_B: dict = None
    part2_normal: dict = None
    part2_normal_locked: dict = None
    part2_normal_finished: dict = None

    part2_hard_A: dict = None
    part2_hard_B: dict = None
    part2_hard: dict = None
    part2_hard_locked: dict = None
    part2_hard_finished: dict = None

    part2_difficulty_normal: dict = None
    part2_difficulty_hard: dict = None

    event_page_main: Page = None
    event_page_main_sign: dict = None
    event_page_main_to_part1: dict = None
    event_page_main_to_part2: dict = None

    event_part1: Page = None
    event_part1_sign: dict = None
    event_part1_to_steps: dict = None

    event_part1_steps: Page = None
    event_part1_steps_sign: dict = None

    event_part2: Page = None
    event_part2_sign: dict = None
    event_part2_to_steps: dict = None

    event_part2_steps: Page = None
    event_part2_steps_sign: dict = None

    page_main_button: dict = None
