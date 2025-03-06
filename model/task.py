from enum import Enum
from typing import Any, Optional

class Task:
    '''
    Represents a task in a real-time system.

    Attributes:
        name (str): Task identifier/name
        bcet (float): Best-case execution time
        wcet (float): Worst-case execution time
        period (float): Task period
        deadline (float): Task relative deadline
        core (int): Core number on which the task is assigned (default: 0)
        priority (float): Task priority (default: 0.0)
        task_type (TaskType): Task type, either TaskType.TT or TaskType.ET (default: TaskType.TT)
        MIT (float): Minimum Inter-arrival Time for sporadic tasks (default: 0.0)
        assigned_server: Assigned server when using polling servers (default: None)
    '''

    def __init__(self, 
                 name: str, 
                 bcet: int,  
                 wcet: int,  
                 period: int,
                 deadline: int,
                 priority: int = 0) -> None:
        """
        Initialize a Task object with several properties.
        
        Args:
            name (str): Task identifier/name
            bcet (int): Best-case execution time
            wcet (int): Worst-case execution time
            period (int): Task period
            deadline (int): Task relative deadline
            priority (int): Task priority (default: 0.0)
        """
        if bcet > wcet:
            raise ValueError("BCET cannot be greater than WCET")
        
        self.name = name
        self.bcet = bcet
        self.wcet = wcet
        self.period = period
        self.deadline = deadline
        self.priority = priority