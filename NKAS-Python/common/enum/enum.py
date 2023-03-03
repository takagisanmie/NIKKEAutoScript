class ImgResult:
    LOCATION = 1
    POSITION = 2
    SIMILARITY = 3
    LOCATION_AND_SIMILARITY = 4
    POSITION_AND_SIMILARITY = 5
    NONE = 0


class OcrResult:
    LOCATION = 1
    TEXT = 2
    LOCATION_AND_TEXT = 3
    POSITION = 4
    LOCATION_AND_POSITION = 5
    ALL_RESULT = 6
    NONE = 0


class AssetResponse:
    ASSET_HIDE = 1
    ASSET_SHOW = 2
    TEXT_HIDE = 3
    TEXT_SHOW = 4
    PAGE_CHANGE = 5
    NONE = 0


class EventType:
    BATTLE = 1
    BOSS = 2
    IMPROVEMENT = 3
    HEALING = 4
    RANDOM = 5
    HARD_BATTLE = 6

    # BATTLE = 2
    # BOSS = 2
    # HEALING = 3
    # HARD_BATTLE = 4
    # IMPROVEMENT = 1
    # RANDOM = 1


class EffectOperationType:
    SAVE = 1


class BattleEventDifficulty:
    NORMAL = 1
    HARD = 2


class TimeoutStrategy:
    THROW_EXCEPTION = 1
    NONE = 0


class EventParameter:
    SMALL = 0
    LARGE = 1

    NORMAL = 0
    HARD = 1

    PART_1 = 1
    PART_2 = 2


class Path:
    CONFIG = './common/config/config.yaml'
    TASK = './common/config/task.yaml'
    SCREENSHOT_PATH = './pic/img.png'
