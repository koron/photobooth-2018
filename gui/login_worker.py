from logging import getLogger, StreamHandler, INFO, DEBUG
import threading

from PyQt5.QtCore import QObject, pyqtSignal
from InstagramAPI import InstagramAPI

handler = StreamHandler()
handler.setLevel(DEBUG)
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

class LoginWorker(QObject):

    loggedIn = pyqtSignal(object)

    def __init__(self, parent, config):
        QObject.__init__(self)
        self.parent = parent
        self.config = config

    def login(self):
        api = InstagramAPI(
                self.config.instagram_username,
                self.config.instagram_password)
        api.login()
        self.loggedIn.emit(api)

    def start(self):
        thread = threading.Thread(target=self.login)
        thread.start()
