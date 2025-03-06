import pytest
from model import Task, TaskSet
from scheduling import RateMonotonic

class TestRateMonotonic:
    def test_assign_priorities(self):
        task1 = Task("Task_1", 5, 10, 100, 100, 0)
        task2 = Task("Task_2", 10, 20, 50, 50, 0)
        task3 = Task("Task_3", 1, 2, 200, 200, 0)
        task4 = Task("Task_4", 3, 6, 50, 50, 0)  # Same period as Task_2
        
        taskset = TaskSet([task1, task2, task3, task4])
        
        rm = RateMonotonic()
        rm.assign_priorities(taskset)
        
        # Tasks with shorter periods should have higher priorities (lower numbers)
        assert taskset.tasks["Task_2"].priority < taskset.tasks["Task_1"].priority
        assert taskset.tasks["Task_1"].priority < taskset.tasks["Task_3"].priority
        
        # Tasks with the same period should have the same priority
        assert taskset.tasks["Task_2"].priority == taskset.tasks["Task_4"].priority
    
    def test_empty_taskset(self):
        taskset = TaskSet()
        rm = RateMonotonic()
        
        # Should not raise an exception
        rm.assign_priorities(taskset)