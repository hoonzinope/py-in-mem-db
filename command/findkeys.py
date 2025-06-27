from command.command import Command
from command.registry import register_command
from logger import logger
import shlex
import re

@register_command("find-keys")
class FindKeys(Command):
    def __init__(self, pattern=None):
        super().__init__()
        self.pattern = pattern
        self.logger = logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.pattern:
            self._log("No pattern provided for finding keys.")
            return "No pattern provided for finding keys."

        if self.memdb.in_load:
            return self._execute_find_keys()

        if memdb.in_transaction:
            return self._execute_find_keys()
        else:
            with self.memdb.lock:
                return self._execute_find_keys()

    # This method is used to find keys in the database that match the given pattern.
    # pattern like "key"(same),
    # option -l or --like and pattern "key*"(like),
    # option -r or --regex and patten "^abc\d+$"(regex)
    def _execute_find_keys(self):
        self.memdb.clean_expired_keys()

        tokens = shlex.split(self.pattern)
        if len(tokens) == 1:
            pattern = tokens[0]
            return self._exact_pattern_execute(pattern)
        elif len(tokens) == 2 and (tokens[0] == "-r" or tokens[0] == "--regex"):
            pattern = tokens[1]
            return self._regex_pattern_execute(pattern)
        elif len(tokens) == 2 and (tokens[0] == "-l" or tokens[0] == "--like"):
            pattern = tokens[1]
            return self._like_pattern_execute(pattern)
        else:
            error_msg = ("Invalid pattern format. Use: "
                         "find-keys <pattern> or "
                         "find-keys -r <regex> or "
                         "find-keys -l <like-pattern>")
            self._log(error_msg)
            return []

    def _regex_pattern_execute(self, pattern : str) -> list:
        try:
            regex_pattern = re.compile(pattern)
            keys = list(self.memdb.data.keys())
            matching_keys = [key for key in keys if regex_pattern.match(key)]
            return matching_keys if matching_keys else []
        except re.error as e:
            self._log(f"Invalid regex pattern: {e}")
            return []

    def _like_pattern_execute(self, pattern : str) -> list:
        try:
            regex_pattern = self._wildcard_to_regex(pattern)
            keys = list(self.memdb.data.keys())
            matching_keys = [key for key in keys if re.match(regex_pattern, key)]
            return matching_keys if matching_keys else []
        except re.error as e:
            self._log(f"Invalid like pattern: {e}")
            return []

    def _exact_pattern_execute(self, pattern : str) -> list:
        keys = list(self.memdb.data.keys())
        matching_keys = [key for key in keys if key == pattern]
        return matching_keys if matching_keys else []

    def _wildcard_to_regex(self, pattern : str) -> str:
        # 예: key* → ^key.*, *key → .*key$, *key* → .*key.*, key? → ^key.$
        regex = "^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".") + "$"
        return regex

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
