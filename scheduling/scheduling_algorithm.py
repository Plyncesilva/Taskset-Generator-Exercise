from abc import ABC, abstractmethod
from model import TaskSet

class SchedulingAlgorithm(ABC):
    """
    Abstract base class for scheduling algorithms.
    All scheduling algorithm implementations must inherit from this class.
    """

    @abstractmethod
    def assign_priorities(self, taskset: TaskSet) -> None:
        """
        Assign priorities to tasks based on the algorithm's policy.
        
        Args:
            taskset: A TaskSet object containing tasks to assign priorities to
        """
        pass
