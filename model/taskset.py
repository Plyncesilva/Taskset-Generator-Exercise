from typing import Dict
from math import lcm
from functools import reduce
import csv
import copy
from .task import Task
import os

class TaskSet:
    '''
    Represents a set of tasks in a real-time system.

    Attributes:
        tasks (Dict[str, Task]): A dictionary of tasks with their names as keys.
        hyperperiod (float): The hyperperiod of the task set.
        worst_case_utilization (float): The worst-case CPU utilization of the task set.
    '''

    def __init__(self, tasks: list[Task] = []) -> None:
        self.tasks: Dict[str, Task] = {task.name: copy.deepcopy(task) for task in tasks}
        self.hyperperiod: float = self.__calculate_hyperperiod()
        self.worst_case_utilization = self.__calculate_utilization()

    def update_properties(self):
        self.hyperperiod = self.__calculate_hyperperiod()
        self.worst_case_utilization = self.__calculate_utilization()

    def add_task(self, task: Task) -> None:
        '''
        Add a task to the task set.
        
        Args:
            task (Task): The task to add to the task set.
        '''

        self.tasks[task.name] = task
        self.update_properties()


    def to_csv(self, folder: str, file_name: str) -> None:
        '''
        Write the TaskSet instance to a CSV file.

        The file is created at the given folder and uses the given file name (with .csv extension).

        Args:
            folder (str): The folder where the CSV file will be saved.
            file_name (str): The base name for the CSV file (without .csv extension).
        '''
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, f"{file_name}.csv")
        headers = ['Task', 'BCET', 'WCET', 'Period', 'Deadline', 'Priority']
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for task in self.tasks.values():
                writer.writerow({
                    'Task': task.name,
                    'BCET': int(task.bcet),
                    'WCET': int(task.wcet),
                    'Period': int(task.period),
                    'Deadline': int(task.deadline),
                    'Priority': int(task.priority)
                })

    def __iter__(self):
        return iter(self.tasks.values())
    
    def __len__(self):
        return len(self.tasks)

    def __calculate_hyperperiod(self) -> float:
        periods = [int(task.period) for task in self.tasks.values()]
        if not periods:
            return 0.0
        
        return reduce(lcm, periods)

    def __calculate_utilization(self) -> float:
        return round(sum(task.wcet / task.period for task in self.tasks.values() if task.period > 0), 2)