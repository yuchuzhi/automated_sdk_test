import six
import logging
from .serialspawn import SerialSpawn
from pexpect.exceptions import TIMEOUT


class AppTest(object):
    def __init__(self, board_obj, *args, **kwargs):
        self.timeout = 3
        self.board = board_obj
        self.expectedPatterns = ["hello world"]
        

    def pre_init(self):
        self.serial = self.board.ser_main
        self.spawn = SerialSpawn(self.serial)

    def interact(self):
        self.spawn.test_expect(self.expectedPatterns, timeout=self.timeout)

    def deinit(self):
        self.spawn.close()
        serial_log = self.spawn.serial.data

        logging.info('{:-^36}'.format(f" serial output of {self.serial.port} "))
        logging.info(serial_log)
        logging.info('{:-^36}'.format(" serial output end  "))
        if self.serial.is_open:
            self.serial.close()
