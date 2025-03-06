import csv
from scheduling import SchedulingAlgorithm, RateMonotonic

class Requirement:
    '''
    A class to represent a task requirement.

    Attributes
    ----------
    name : str
        The name of the requirement.
    size : int
        The size of the taskset.
    utilization : float
        The utilization of the taskset.
    unique_periods : bool
        Whether the taskset has unique periods or not.
    algorithm : SchedulingAlgorithm
        The scheduling algorithm used to assign priorities.
    '''

    def __init__(self, 
                 name: str, size: int, 
                 utilization: float, 
                 unique_periods: bool,
                 algorithm: SchedulingAlgorithm
    ):
        self.name = name
        self.size = size
        self.utilization = utilization
        self.unique_periods = unique_periods
        self.algorithm = algorithm

    def __repr__(self):
        return (f"Requirement(name={self.name}, size={self.size}, utilization={self.utilization}, "
                f"unique_periods={self.unique_periods},"
                f"algorithm={self.algorithm})")

class TaskRequirements:
    '''
    A class to represent a set of task requirements.

    Attributes
    ----------
    requirements : list
        A list of Requirement objects
    '''

    def __init__(self, requirements=None):
        if requirements is None:
            requirements = []
        self.requirements = requirements

    @classmethod
    def from_csv(cls, file_path):
        requirements = []
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                algorithm = None
                if row['PriorityAssignment'].strip() == 'RM':
                    algorithm = RateMonotonic()

                # Create a dictionary with mandatory arguments
                req_args = {
                    'name': row['Name'],
                    'size': int(row['Size'].strip()),
                    'utilization': float(row['Utilization'].strip()),
                    'unique_periods': row['UniquePeriods'].strip().lower() == 'true',
                    'algorithm': algorithm,
                }
                
                requirement = Requirement(**req_args)
                requirements.append(requirement)
        return cls(requirements)

    def __repr__(self):
        return f"TestRequirements(requirements={self.requirements})"

    def __iter__(self):
        return iter(self.requirements)
