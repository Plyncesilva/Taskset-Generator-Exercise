import pytest
import os
import csv
import tempfile
from generator.task_requirements import TaskRequirements, Requirement
from scheduling import RateMonotonic

class TestTaskRequirements:
    def test_init_empty_requirements(self):
        reqs = TaskRequirements()
        assert len(reqs.requirements) == 0
    
    def test_init_with_requirements(self):
        rm = RateMonotonic()
        req = Requirement(name="Test", size=5, utilization=0.5, unique_periods=True, algorithm=rm)
        reqs = TaskRequirements([req])
        assert len(reqs.requirements) == 1
        assert reqs.requirements[0].name == "Test"
    
    def test_from_csv(self):
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("Name,Size,Utilization,UniquePeriods,PriorityAssignment\n")
            f.write("Test1,5,0.5,true,RM\n")
            f.write("Test2,10,0.8,false,RM\n")
            csv_path = f.name
            
        try:
            reqs = TaskRequirements.from_csv(csv_path)
            assert len(reqs.requirements) == 2
            assert reqs.requirements[0].name == "Test1"
            assert reqs.requirements[0].size == 5
            assert reqs.requirements[0].utilization == 0.5
            assert reqs.requirements[0].unique_periods == True
            assert isinstance(reqs.requirements[0].algorithm, RateMonotonic)
            
            assert reqs.requirements[1].name == "Test2"
            assert reqs.requirements[1].size == 10
            assert reqs.requirements[1].utilization == 0.8
            assert reqs.requirements[1].unique_periods == False
            assert isinstance(reqs.requirements[1].algorithm, RateMonotonic)
        finally:
            os.remove(csv_path)
    
    def test_repr(self):
        rm = RateMonotonic()
        req = Requirement(name="Test", size=5, utilization=0.5, unique_periods=True, algorithm=rm)
        reqs = TaskRequirements([req])
        repr_str = repr(reqs)
        assert "TestRequirements" in repr_str
        assert "Test" in repr_str
    
    def test_iteration(self):
        rm = RateMonotonic()
        req1 = Requirement(name="Test1", size=5, utilization=0.5, unique_periods=True, algorithm=rm)
        req2 = Requirement(name="Test2", size=10, utilization=0.8, unique_periods=False, algorithm=rm)
        reqs = TaskRequirements([req1, req2])
        
        requirements = list(reqs)
        assert len(requirements) == 2
        assert requirements[0].name == "Test1"
        assert requirements[1].name == "Test2"