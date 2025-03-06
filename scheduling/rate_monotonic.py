from model import TaskSet
from .scheduling_algorithm import SchedulingAlgorithm

class RateMonotonic(SchedulingAlgorithm):
    """
    Rate Monotonic Scheduling Algorithm implementation.
    Assigns priorities to tasks based on their periods - shorter period means higher priority.
    """

    def assign_priorities(self, taskset: TaskSet) -> None:
        """
        Assign priorities to tasks based on their periods.

        Args:
            taskset: A TaskSet object containing tasks to assign priorities to
        """
        sorted_tasks = sorted(taskset, key=lambda task: task.period)
        for i, task in enumerate(sorted_tasks):
            # Maintain equal priority for equal periods
            if i > 0 and task.period == sorted_tasks[i - 1].period:
                task.priority = sorted_tasks[i - 1].priority
            else:
                task.priority = i
