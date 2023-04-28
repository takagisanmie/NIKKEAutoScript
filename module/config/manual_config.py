class ManualConfig:
    SCHEDULER_PRIORITY = """
       Restart
       > Reward > Destroy > Commission > Conversation > RookieArena > SimulationRoom
       """

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

    @property
    def SERVER(self):
        return 'cn'
