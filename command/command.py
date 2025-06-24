from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self, memdb, persistence_manager): #, *args, **kwargs
        pass