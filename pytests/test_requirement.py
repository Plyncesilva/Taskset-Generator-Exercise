import pytest
from generator.task_requirements import Requirement
from scheduling import RateMonotonic

class TestRequirement:
    def test_init(self):
        rm = RateMonotonic()
        req = Requirement(name="Test", size=5, utilization=0.5, unique_periods=True, algorithm=rm)
        
        assert req.name == "Test"
        assert req.size == 5
        assert req.utilization == 0.5
        assert req.unique_periods == True
        assert req.algorithm == rm
    
    def test_repr(self):
        rm = RateMonotonic()
        req = Requirement(name="Test", size=5, utilization=0.5, unique_periods=True, algorithm=rm)
        
        repr_str = repr(req)
        assert "Requirement" in repr_str
        assert "name=Test" in repr_str
        assert "size=5" in repr_str
        assert "utilization=0.5" in repr_str
        assert "unique_periods=True" in repr_str
        assert "algorithm=" in repr_str