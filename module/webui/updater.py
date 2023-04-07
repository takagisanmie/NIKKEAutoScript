from deploy.config import ExecutionError
from deploy.git import GitManager
from deploy.utils import DEPLOY_CONFIG
from module.base.retry import retry
from module.logger import logger


class Updater(GitManager):
    def __init__(self, file=DEPLOY_CONFIG):
        super().__init__(file=file)

    @retry(ExecutionError, tries=3, delay=5, logger=None)
    def git_install(self):
        return super().git_install()

    def update(self):
        logger.hr("Run update")
        try:
            self.git_install()
        except ExecutionError:
            return False
        return True


updater = Updater()

if __name__ == "__main__":
    updater.update()
