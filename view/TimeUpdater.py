"""
view/TimeUpdater.py

Author:
    Zachary Smith
"""

from PyQt5.QtCore import QRunnable, pyqtSlot
import logging
from datetime import datetime
from time import sleep

from view.SeaLionThread import WorkerSignals

_LOGGER = logging.getLogger()


class TimeUpdater(QRunnable):
    def __init__(self, gui_instance):
        """
        Constructor
        """
        super(TimeUpdater, self).__init__()
        self.signals = WorkerSignals()
        self.gui = gui_instance

    @pyqtSlot()
    def run(self):
        while self.gui.testing:
            sleep(1)
            difference = datetime.now() - self.gui.test_start
            difference = divmod(difference.total_seconds(), 60)
            self.signals.status_bar.emit('{} min {} sec'.format(int(difference[0]),
                                                                int(difference[1])))
        self.signals.status_bar.emit('Done: {} min {} sec'.format(int(difference[0]),
                                                                  int(difference[1])))
