from abc import ABC, abstractmethod

class Command(ABC):
    def __init__(self):
        self.memdb = None
        self.persistence_manager = None
        self.command_parser = None

    @abstractmethod
    def execute(self, memdb, persistence_manager, session_id=None): #, *args, **kwargs
        pass