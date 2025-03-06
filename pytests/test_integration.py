import pytest
import os
import tempfile
import csv
from generator import TaskGenerator, TaskRequirements
from model import TaskSet
from scheduling import RateMonotonic

class TestIntegration:
    @pytest.fixture
    def tmp_config_file(self):
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("Name,Size,Utilization,UniquePeriods,PriorityAssignment\n")
            f.write("Test_Low_Utilization,3,0.3,true,RM\n")
            f.write("Test_Medium_Utilization,5,0.5,false,RM\n")
            f.write("Test_High_Utilization,2,0.8,true,RM\n")
            csv_path = f.name
            
        yield csv_path
        os.remove(csv_path)
    
    @pytest.fixture
    def output_dir(self):
        # Create a temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_end_to_end_flow(self, tmp_config_file, output_dir):
        # Load requirements from CSV
        requirements = TaskRequirements.from_csv(tmp_config_file)
        assert len(requirements.requirements) == 3
        
        # Initialize generator
        generator = TaskGenerator(requirements, output_dir)
        
        # Generate tasksets for all requirements
        generator.generate_tasksets()
        
        # Check that output directories and files are created
        assert os.path.exists(f"{output_dir}/0.3_utilization/")
        assert os.path.exists(f"{output_dir}/0.5_utilization/")
        assert os.path.exists(f"{output_dir}/0.8_utilization/")
        
        # Check files are created
        assert os.path.isfile(f"{output_dir}/0.3_utilization/Test_Low_Utilization_taskset.csv")
        assert os.path.isfile(f"{output_dir}/0.5_utilization/Test_Medium_Utilization_taskset.csv")
        assert os.path.isfile(f"{output_dir}/0.8_utilization/Test_High_Utilization_taskset.csv")
        
        # Check CSV contents of one file
        with open(f"{output_dir}/0.3_utilization/Test_Low_Utilization_taskset.csv", 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3  # 3 tasks as specified
            
            # Verify that periods are unique (as requested)
            periods = [int(row['Period']) for row in rows]
            assert len(periods) == len(set(periods))
            
            # Calculate utilization to verify it's close to 0.3
            utilization = sum([int(row['WCET']) / int(row['Period']) for row in rows])
            assert abs(utilization - 0.3) <= 0.05