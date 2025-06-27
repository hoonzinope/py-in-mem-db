from command.command import Command
from command.registry import register_command
from logger import logger
import shlex
import argparse
import re

@register_command("find")
class Find(Command):
    def __init__(self, pattern=None):
        super().__init__()
        self.pattern = pattern
        self.logger = logger(self.__class__.__name__)
        self.error_msg =  ("Invalid pattern format. Use: "
                         "find -[k,v] <pattern> or "
                         "find -[k,v] -r <regex> or "
                         "find -[k,v] -l <like-pattern>")
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-k', '--key', action='store_true', help='Find keys matching the pattern')
        self.parser.add_argument('-v', '--value', action='store_true', help='Find values matching the pattern')
        self.parser.add_argument('-r', '--regex', type=str, help='Use regex for matching')
        self.parser.add_argument('-l', '--like', type=str, help='Use like pattern for matching')
        self.parser.add_argument('pattern', nargs='?', default=None)  # 옵션 없이 패턴만 올 경우
        self.args = None  # To store parsed arguments

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.pattern:
            self._log("No pattern provided for finding keys or values.")
            return "No pattern provided for finding keys."

        if memdb.in_load:
            return self._execute_find()

        if memdb.in_transaction:
            return self._execute_find()
        else:
            with memdb.lock:
                return self._execute_find()

    # find keys or values in the database that match the given pattern.
    # find -k <pattern> for keys,
    # find -v <pattern> for values,
    def _execute_find(self):
        self.memdb.clean_expired_keys()
        tokens = shlex.split(self.pattern)
        self.args = self.parser.parse_args(tokens)
        check_list = []
        if self.args.key:
            check_list = list(self.memdb.data.keys())
        elif self.args.value:
            check_list = list([v['value'] for v in self.memdb.data.values()])
        else:
            self._log(self.error_msg)
            return []
        return self._pattern_execute(tokens, check_list)

    def _pattern_execute(self, tokens: list, check_list: list) -> list:
        if self.args.like is not None:
            return self._like_pattern_execute(self.args.like, check_list)
        elif self.args.regex is not None:
            return self._regex_pattern_execute(self.args.regex, check_list)
        elif len(tokens) == 2:
            return self._exact_pattern_execute(tokens[1], check_list)
        else:
            self._log(self.error_msg)
            return []

    def _regex_pattern_execute(self, pattern: str, checklist : list) -> list:
        try:
            regex_pattern = re.compile(pattern)
            matching_keys = [key for key in checklist if regex_pattern.match(key)]
            return matching_keys if matching_keys else []
        except re.error as e:
            self._log(f"Invalid regex pattern: {e}")
            return []

    def _like_pattern_execute(self, pattern: str, checklist : list) -> list:
        try:
            regex_pattern = self._wildcard_to_regex(pattern)
            matching_keys = [key for key in checklist if re.match(regex_pattern, key)]
            return matching_keys if matching_keys else []
        except re.error as e:
            self._log(f"Invalid like pattern: {e}")
            return []

    def _exact_pattern_execute(self, pattern: str, checklist : list) -> list:
        matching_keys = [key for key in checklist if key == pattern]
        return matching_keys if matching_keys else []

    def _wildcard_to_regex(self, pattern: str) -> str:
        # 예: key* → ^key.*, *key → .*key$, *key* → .*key.*, key? → ^key.$
        regex = "^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".") + "$"
        return regex

    def _log(self, message):
        self.logger.log(message)
