from command.command import Command
from command.registry import register_command


@register_command("help")
class Help(Command):
    def __init__(self, original_command: str = None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        return (
            "Commands:\n"
            "put <key> <value> <expiration_time> - Store a value with a key and an expiration time in seconds (default 7 seconds)\n"
            "get <key> - Retrieve a value by key \n"
            "delete <key> - Remove a key-value pair\n"
            "clear - Clear the database\n"
            "exists <key> - Check if a key exists\n"
            "keys - List all keys\n"
            "values - List all values\n"
            "items - List all key-value pairs\n"
            "size - Get the number of items in the database\n"
            "begin - Start a transaction\n"
            "commit - Commit the current transaction\n"
            "rollback - Rollback the current transaction\n"
            "exit - Exit the command interface\n"
            "alias <alias_name> <command> - Create an alias for a command\n"
            "show-alias - Show all aliases\n"
            "reset-alias - Reset all aliases\n"
            "batch <commands> - Execute a batch of commands\n"
            "find <commands> - Find keys based on a pattern\n"
        )