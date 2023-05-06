from datetime import datetime, timedelta


class ManualConfig:
    SCHEDULER_PRIORITY = """
       Restart
       > Reward > Destroy > Commission > Shop > RubbishShop > Conversation > RookieArena > SimulationRoom > TribeTower > Event >  Daily > MissionPass > Liberation
       """

    GENERAL_SHOP_PRIORITY = """GRATIS"""

    RUBBISH_SHOP_PRIORITY = """
       GEM
       > CORE_DUST_CASE
       """

    ARENA_SHOP_PRIORITY = """"""

    GENERAL_SHOP_PRODUCT = {
        'GRATIS': 1,
    }

    RUBBISH_SHOP_PRODUCT = {
        'GEM': 1,
        'CORE_DUST_CASE': 2,
        'CREDIT_CASE': 2,
        'BATTLE_DATA_SET_CASE': 2,
        'GENERAL_TICKET': 1,
        'ELYSION_TICKET': 1,
        'MISSILIS_TICKET': 1,
        'TETRA_TICKET': 1,
        'PILGRIM_TICKET': 1,
        'ABNORMAL_TICKET': 1,
    }

    ARENA_SHOP_PRODUCT = {
        'ELECTRIC_CODE': 1,
        'FIRE_CODE': 1,
        'IRON_CODE': 1,
        'WATER_CODE': 1,
        'WIND_CODE': 1,
        'MANUAL_SELECTION_BOX': 1,
    }

    FORWARD_PORT_RANGE = (20000, 21000)

    BUTTON_OFFSET = 30
    BUTTON_MATCH_SIMILARITY = 0.85
    COLOR_SIMILAR_THRESHOLD = 10

    WAIT_BEFORE_SAVING_SCREEN_SHOT = 1

    ASSETS_FOLDER = './assets'

    DROIDCAST_FILEPATH_LOCAL = './bin/DroidCast/DroidCast-debug-1.1.0.apk'
    DROIDCAST_FILEPATH_REMOTE = '/data/local/tmp/DroidCast.apk'

    DROIDCAST_RAW_FILEPATH_LOCAL = './bin/DroidCast/DroidCastS-release-1.1.5.apk'
    DROIDCAST_RAW_FILEPATH_REMOTE = '/data/local/tmp/DroidCastS.apk'

    EVENTS = [
        {
            'event_id': 'event_1',
            'event_name': 'OVER ZONE',
            # large evnet
            'event_type': 1,
            'event_duration': timedelta(days=21),
            # UTC+8 2023-04-27 06:00:00
            'event_update_date': datetime(2023, 4, 27, 4)
        }
    ]

    Error_ScreenshotLength = 1

    @property
    def SERVER(self):
        return 'cn'
