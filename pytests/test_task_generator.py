import pytest
import os
import shutil
import tempfile
from generator import TaskGenerator, TaskRequirements, Requirement
from model import TaskSet
from scheduling import RateMonotonic

class TestTaskGenerator:
    @pytest.fixture
    def basic_requirements(self):
        rm = RateMonotonic()
        req1 = Requirement(name="Test1", size=5, utilization=0.5, unique_periods=False, algorithm=rm)
        req2 = Requirement(name="Test2", size=3, utilization=0.8, unique_periods=True, algorithm=rm)
        return TaskRequirements([req1, req2])
    
    @pytest.fixture
    def output_dir(self):
        # Create a temporary output directory
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_init(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        assert generator.test_requirements == basic_requirements
        assert generator.output_dir == output_dir
    
    def test_generate_taskset(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        # Test generating a taskset for the first requirement
        taskset = generator.generate_taskset(basic_requirements.requirements[0])
        
        assert isinstance(taskset, TaskSet)
        assert len(taskset) == 5  # Size specified in the requirement
        
        # Check utilization is close to the required value
        assert abs(taskset.worst_case_utilization - 0.5) <= 0.05
    
    def test_generate_unique_periods(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        # Test generating a taskset with unique periods
        taskset = generator.generate_taskset(basic_requirements.requirements[1])
        
        # Check that periods are unique
        periods = [task.period for task in taskset]
        assert len(periods) == len(set(periods))
    
    def test_verify_requirement_valid(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        # This should not raise an exception
        generator._TaskGenerator__verify_requirement(basic_requirements.requirements[0])
    
    def test_verify_requirement_invalid_name(self, output_dir):
        rm = RateMonotonic()
        # Name is not a string
        req = Requirement(name=123, size=5, utilization=0.5, unique_periods=True, algorithm=rm)
        generator = TaskGenerator(TaskRequirements([req]), output_dir)
        
        with pytest.raises(ValueError, match="Name must be a string"):
            generator._TaskGenerator__verify_requirement(req)
    
    def test_verify_requirement_invalid_size(self, output_dir):
        rm = RateMonotonic()
        # Size is less than 1
        req = Requirement(name="Test", size=0, utilization=0.5, unique_periods=True, algorithm=rm)
        generator = TaskGenerator(TaskRequirements([req]), output_dir)
        
        with pytest.raises(ValueError, match="Number of tasks must be at least 1"):
            generator._TaskGenerator__verify_requirement(req)
    
    def test_verify_requirement_invalid_utilization(self, output_dir):
        rm = RateMonotonic()
        # Utilization is negative
        req = Requirement(name="Test", size=5, utilization=-0.1, unique_periods=True, algorithm=rm)
        generator = TaskGenerator(TaskRequirements([req]), output_dir)
        
        with pytest.raises(ValueError, match="Utilization must be a positive float"):
            generator._TaskGenerator__verify_requirement(req)
    
    def test_find_integer_n(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        # Test with simple values
        assert generator._TaskGenerator__find_integer_n(0.5) == 2
        assert generator._TaskGenerator__find_integer_n(0.25) == 4
        assert generator._TaskGenerator__find_integer_n(0.2) == 5
        assert generator._TaskGenerator__find_integer_n(0.75) == 4
    
    def test_generate_utilization(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        # Generate utilization values for 5 tasks with total utilization 0.5
        utilization_values = generator._TaskGenerator__generate_utilization(5, 0.5, 1.0)
        
        assert len(utilization_values) == 5
        assert abs(sum(utilization_values) - 0.5) < 0.01  # Sum should be close to 0.5
        assert all(u >= generator.MIN_UTILIZATION for u in utilization_values)  # All values should be at least MIN_UTILIZATION
        assert all(u <= 1.0 for u in utilization_values)  # All values should be at most 1.0
    
    def test_generate_periods(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        # Generate periods for 5 tasks with given utilization values
        utilization_values = [0.1, 0.1, 0.1, 0.1, 0.1]
        
        # Test with non-unique periods
        periods = generator._TaskGenerator__generate_periods(False, utilization_values, RateMonotonic())
        assert len(periods) == 5
        
        # Test with unique periods
        periods = generator._TaskGenerator__generate_periods(True, utilization_values, RateMonotonic())
        assert len(periods) == 5
        assert len(set(periods)) == 5  # All periods should be unique
    
    def test_create_taskset(self, basic_requirements, output_dir):
        generator = TaskGenerator(basic_requirements, output_dir)
        
        utilization_values = [0.1, 0.2, 0.2]
        periods = [10, 20, 30]
        
        taskset = generator._TaskGenerator__create_taskset(utilization_values, periods)
        
        assert len(taskset) == 3
        assert taskset.tasks["Task_0"].period == 10
        assert taskset.tasks["Task_1"].period == 20
        assert taskset.tasks["Task_2"].period == 30
        
        # Check that WCETs are correctly calculated
        assert taskset.tasks["Task_0"].wcet == 1  # 10 * 0.1 = 1
        assert taskset.tasks["Task_1"].wcet == 4  # 20 * 0.2 = 4
        assert taskset.tasks["Task_2"].wcet == 6  # 30 * 0.2 = 6