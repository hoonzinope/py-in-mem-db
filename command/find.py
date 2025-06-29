from command.command import Command
from command.registry import register_command
from logger import Logger
import shlex
import argparse
import re
from response import Response, STATUS_CODE
import time

@register_command("find")
class Find(Command):
    def __init__(self, pattern=None):
        super().__init__()
        self.pattern = pattern
        self.logger = Logger.get_logger()
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

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.pattern:
            msg = "No pattern provided for finding keys or values."
            self._log(msg)
            return self._error_response(msg)

        if memdb.in_load:
            return self._execute_find()

        if session_id not in memdb.in_tx:
            # If not in transaction, we need to lock the database
            with memdb.lock:
                return self._execute_find()
        else:
            # If in transaction, we can append the command to the transaction list
            self.memdb.tx_commands[session_id].append(self.pattern)
            return self._execute_find_in_transaction(session_id)

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

    def _execute_find_in_transaction(self, session_id):
        copy = self.memdb.tx_data[session_id]["copy"]
        snapshot = self.memdb.tx_data[session_id]["snapshot"]

        tokens = shlex.split(self.pattern)
        self.args = self.parser.parse_args(tokens)
        check_list = []
        if self.args.key:
            for key in snapshot.keys():
                if key not in copy:
                    if snapshot[key]['expiration_time'] is None or snapshot[key]['expiration_time'] > time.time():
                        copy[key] = snapshot[key]
                        check_list.append(key)
                else:
                    if copy[key]["expiration_time"] is None or copy[key]["expiration_time"] > time.time():
                        check_list.append(key)
                    else:
                        del copy[key]
        elif self.args.value:
            for key, value in snapshot.items():
                if key not in copy:
                    if value['expiration_time'] is None or value['expiration_time'] > time.time():
                        copy[key] = value
                        check_list.append(value['value'])
                else:
                    if copy[key]["expiration_time"] is None or copy[key]["expiration_time"] > time.time():
                        check_list.append(copy[key]["value"])
                    else:
                        del copy[key]
        else:
            self._log(self.error_msg)
            check_list = []
        return self._pattern_execute(tokens, check_list)

    def _pattern_execute(self, tokens: list, check_list: list) -> Response:
        if self.args.like is not None:
            return self._like_pattern_execute(self.args.like, check_list)
        elif self.args.regex is not None:
            return self._regex_pattern_execute(self.args.regex, check_list)
        elif len(tokens) == 2:
            return self._exact_pattern_execute(tokens[1], check_list)
        else:
            self._log(self.error_msg)
            return []

    def _regex_pattern_execute(self, pattern: str, checklist : list) -> Response:
        try:
            regex_pattern = re.compile(pattern)
            matching_keys = [key for key in checklist if regex_pattern.match(key)]
            return self._success_response(matching_keys)
        except re.error as e:
            self._log(f"Invalid regex pattern: {e}")
            return self._error_response(f"Invalid regex pattern: {e}")

    def _like_pattern_execute(self, pattern: str, checklist : list) -> Response:
        try:
            regex_pattern = self._wildcard_to_regex(pattern)
            matching_keys = [key for key in checklist if re.match(regex_pattern, key)]
            return self._success_response(matching_keys)
        except re.error as e:
            self._log(f"Invalid like pattern: {e}")
            return self._error_response(f"Invalid like pattern: {e}")

    def _exact_pattern_execute(self, pattern: str, checklist : list) -> Response:
        matching_keys = [key for key in checklist if key == pattern]
        return self._success_response(matching_keys)

    def _wildcard_to_regex(self, pattern: str) -> str:
        # 예: key* → ^key.*, *key → .*key$, *key* → .*key.*, key? → ^key.$
        regex = "^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".") + "$"
        return regex

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)

    def _error_response(self, message, data=None):
        return Response(
            status_code=STATUS_CODE["BAD_REQUEST"],
            message=message,
            data=data
        )

    def _success_response(self, data):
        return Response(
            status_code=STATUS_CODE["OK"],
            message="Find command executed successfully",
            data=data
        )
