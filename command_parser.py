from command.registry import parse_command
from logger import logger

class Parser:
    def __init__(self):
        self.logger = logger.get_logger()

    def parse(self, cmd):
        self.logger.append_usage_log(cmd, name=self.__class__.__name__)
        return parse_command(cmd)