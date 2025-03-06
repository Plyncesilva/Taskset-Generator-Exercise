import pytest
from model import Task, TaskSet
import os
import csv

class TestTask:
    def test_task_initialization(self):
        task = Task("Task_1", 5, 10, 100, 100, 1)
        
        assert task.name == "Task_1"
        assert task.bcet == 5
        assert task.wcet == 10
        assert task.period == 100
        assert task.deadline == 100
        assert task.priority == 1
    
    def test_bcet_larger_than_wcet_raises_error(self):
        with pytest.raises(ValueError):
            Task("Task_1", 15, 10, 100, 100, 1)

class TestTaskSet:
    def test_empty_taskset(self):
        taskset = TaskSet()
        
        assert len(taskset) == 0
        assert taskset.hyperperiod == 0.0
        assert taskset.worst_case_utilization == 0
    
    def test_taskset_with_tasks(self):
        task1 = Task("Task_1", 5, 10, 100, 100, 1)
        task2 = Task("Task_2", 10, 20, 200, 200, 2)
        
        taskset = TaskSet([task1, task2])
        
        assert len(taskset) == 2
        assert "Task_1" in taskset.tasks
        assert "Task_2" in taskset.tasks
        assert taskset.hyperperiod == 200  # lcm of 100 and 200
        assert taskset.worst_case_utilization == 0.2  # 10/100 + 20/200 = 0.1 + 0.1 = 0.2
    
    def test_add_task(self):
        taskset = TaskSet()
        task = Task("Task_1", 5, 10, 100, 100, 1)
        
        taskset.add_task(task)
        
        assert len(taskset) == 1
        assert "Task_1" in taskset.tasks
        assert taskset.hyperperiod == 100
        assert taskset.worst_case_utilization == 0.1
    
    def test_taskset_iteration(self):
        task1 = Task("Task_1", 5, 10, 100, 100, 1)
        task2 = Task("Task_2", 10, 20, 200, 200, 2)
        
        taskset = TaskSet([task1, task2])
        
        tasks = list(taskset)
        assert len(tasks) == 2
        task_names = [task.name for task in tasks]
        assert "Task_1" in task_names
        assert "Task_2" in task_names
    
    def test_to_csv(self, tmpdir):
        task1 = Task("Task_1", 5, 10, 100, 100, 1)
        task2 = Task("Task_2", 10, 20, 200, 200, 2)
        
        taskset = TaskSet([task1, task2])
        
        output_folder = str(tmpdir)
        taskset.to_csv(output_folder, "test_taskset")
        
        # Check if the file exists
        csv_path = f"{output_folder}/test_taskset.csv"
        assert os.path.isfile(csv_path)
        
        # Read the CSV file and check its contents
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            
            assert rows[0]['Task'] == 'Task_1'
            assert int(rows[0]['BCET']) == 5
            assert int(rows[0]['WCET']) == 10
            assert int(rows[0]['Period']) == 100
            assert int(rows[0]['Deadline']) == 100
            assert int(rows[0]['Priority']) == 1
            
            assert rows[1]['Task'] == 'Task_2'
            assert int(rows[1]['BCET']) == 10
            assert int(rows[1]['WCET']) == 20
            assert int(rows[1]['Period']) == 200
            assert int(rows[1]['Deadline']) == 200
            assert int(rows[1]['Priority']) == 2