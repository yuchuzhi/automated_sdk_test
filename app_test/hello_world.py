import time
from .apptest_base import AppTest



class Case(AppTest):
    def __init__(self, board_obj, *args, **kwargs):
        super().__init__(board_obj, *args, **kwargs)
        self.expectedPatterns = ["hello world"]

    def interact(self):
        super().interact()
        self.spawn.write(r"abcDEF 012345 ~!@#$%\r\n")
        self.spawn.test_expect([r"abcDEF 012345 ~\!@#\$%"], timeout=self.timeout)   
