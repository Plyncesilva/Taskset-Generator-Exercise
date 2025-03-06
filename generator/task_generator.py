import random
from .task_requirements import TaskRequirements, Requirement
from model import Task, TaskSet
from scheduling import SchedulingAlgorithm
import itertools
import sys
import threading
import time
from fractions import Fraction

class TaskGenerator:
    MAX_UTILIZATION = 1.0
    MIN_UTILIZATION = 0.01

    def __init__(self, test_requirements: TaskRequirements, output_dir: str):
        self.test_requirements = test_requirements
        self.output_dir = output_dir

    def generate_taskset(self, req: Requirement) -> TaskSet:
        '''
        Generate a taskset based on the given requirements.

        Parameters:
            req (Requirement): The requirements for the taskset.

        Returns:
            TaskSet: The generated taskset.
        '''
        
        # Verify input requirement before generating taskset
        self.__verify_requirement(req)
        
        done = False
        threshold = 0

        while not done:
            
            # Generate random utilization values for each task
            utilization = self.__generate_utilization(req.size, req.utilization, self.MAX_UTILIZATION)

            # Generate the periods divisible by the utilizations for simpler WCET
            periods = self.__generate_periods(req.unique_periods, utilization, req.algorithm)

            # Built the taskset based on the generated utilization and periods
            taskset = self.__create_taskset(utilization, periods)

            # Check if the taskset meets the requirements and respects deviation threshold
            util_deviation = abs(taskset.worst_case_utilization - req.utilization)
            if len(taskset) == req.size and util_deviation <= threshold:
                done = True
            else:
                threshold += 0.01
                continue

        # Assign priorities to the tasks if an algorithm is provided
        if req.algorithm != None:
            req.algorithm.assign_priorities(taskset)

        return taskset
   
    def generate_tasksets(self) -> None:
        ''' 
        Generate tasksets for all test requirements and store them in the output directory.
        '''

        for req in self.test_requirements:
            print() # Loading animation
            loading_thread, stop_loading = self.__animate_loading(f'Generating taskset for test requirements: \033[92m{req.name}\033[0m')

            try:
                taskset = self.generate_taskset(req)
            except Exception as e:
                print(f"\n\033[91mError: {e}\033[0m")
                stop_loading()
                loading_thread.join()
                continue

            file_path = f"{self.output_dir}/{req.utilization}_utilization/"

            self.__pretty_print_results(req, taskset, file_path)

            taskset.to_csv(
                file_path,
                f"{req.name}_taskset"
            )

            stop_loading()
            loading_thread.join()
        
        print("\n\033[92mDone!\033[0m")

    def __generate_utilization(self, numTasks: int, utilization: float, taskUtilizationLimit: float) -> list[float]:
        '''
        Generate utilization values for the tasks based on the given requirements.

        Parameters:
            numTasks (int): The number of tasks.
            utilization (float): The total utilization of the tasks.
            taskUtilizationLimit (float): The maximum utilization of a task.

        Returns:
            list[float]: The generated utilization values for the tasks.
        '''
        
        # Ensure the requested total utilization is enough to give each task at least 1% utilization
        if utilization < numTasks * self.MIN_UTILIZATION:
            raise ValueError("Number of tasks and total utilization must be such that each task can have at least 1% utilization.")

        # The baseline is allocated to each task
        baseline = [self.MIN_UTILIZATION] * numTasks
        remainder = utilization - (self.MIN_UTILIZATION * numTasks)

        while True:
            # Generate a random partition of the remaining utilization over the tasks
            random_parts = [random.random() for _ in range(numTasks)]
            sum_random = sum(random_parts)
            # Calculate additional utilization for each task based on the random weights
            additions = [(part / sum_random) * remainder for part in random_parts]

            # Sum baseline and addition, rounded to 2 decimals
            utilizationValues = [round(base + add, 2) for base, add in zip(baseline, additions)]
            # Adjust the last task to ensure the total sums exactly to the requested utilization
            diff = round(utilization - sum(utilizationValues), 2)
            utilizationValues[-1] = round(utilizationValues[-1] + diff, 2)

            # Ensure the last task still meets the minimum utilization
            if utilizationValues[-1] < self.MIN_UTILIZATION:
                continue

            # Check that no task exceeds the provided taskUtilizationLimit
            if all(u <= taskUtilizationLimit for u in utilizationValues):
                break

        return utilizationValues
    
    def __generate_periods(self, unique: bool, utilization: list[float], algorithm: SchedulingAlgorithm) -> list[int]:
        '''
        Generate periods for the tasks based on the given utilization values and requirements.

        Parameters:
            unique (bool): Whether the periods should be unique.
            utilization (list[float]): The utilization values for the tasks.
            algorithm (SchedulingAlgorithm): The priority assignment algorithm.

        Returns:
            list[int]: The generated periods for the tasks.
        '''


        def scale_up_duplicates(periods: list[int]) -> None:
            '''
            Scale up the periods of tasks that have the same period to make them unique.
            '''
            duplicates = {}
            for idx, p in enumerate(periods):
                duplicates.setdefault(p, []).append(idx)
            for p, indices in duplicates.items():
                if len(indices) > 1:
                    for i in indices[1:]:
                        scale_factor = random.randint(2, 3)
                        periods[i] = periods[i] * scale_factor

        periods = [ self.__find_integer_n(u) for u in utilization ]
        # Ensure periods are unique if requested
        if unique:
            while len(set(periods)) != len(periods):
                scale_up_duplicates(periods)

        return periods

    def __animate_loading(self, text):
        done_event = threading.Event()

        def animate():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if done_event.is_set():
                    break
                sys.stdout.write(f'\r{text} {c}')
                sys.stdout.flush()
                time.sleep(0.1)

        t = threading.Thread(target=animate)
        t.start()
        return t, done_event.set
    
    def __pretty_print_results(self, req: Requirement, taskset: TaskSet, file_path: str) -> None:
        actual_utilization = sum(task.wcet / task.period for task in taskset)
        utilization_deviation = round(abs(actual_utilization - req.utilization), 2)
        periods = [task.period for task in taskset]

        print(f"\n{'='*40}")
        print(f"Number of tasks: {req.size}")
        deviation_str = f"{utilization_deviation:.2f}"
        if utilization_deviation > 0:
            deviation_str = f"\033[93m{deviation_str}\033[0m"
        print(f"Utilization (requested/taskset/deviation): {req.utilization:.2f}/{actual_utilization:.2f}/{deviation_str}")
        print(f"Hyperperiod: {int(taskset.hyperperiod)}")
        unique_status = len(periods) == len(set(periods))
        if unique_status != req.unique_periods:
            print(f"Unique periods: \033[93m{unique_status}\033[0m")
        else:
            print(f"Unique periods: {unique_status}")
        
        # Check if periods are actually unique
        if req.unique_periods and len(periods) != len(set(periods)):
            print(f"\033[93mWarning: Requested unique periods not possible for this request!\033[0m")
        print(f"{'='*40}\n")
        print(f"Taskset stored in: \033[92m{file_path}{req.name}_taskset.csv\033[0m")

    def __verify_requirement(self, req: Requirement) -> None:
        algorithm_options = "\n\tOptions:\n\t\t- RM: Rate Monotonic"
        
        # Name
        if not isinstance(req.name, str):
            raise ValueError("Name must be a string.")
        # Size
        if req.size < 1:
            raise ValueError("Number of tasks must be at least 1.")
        if not isinstance(req.size, int):
            raise ValueError("Number of tasks must be an integer.")
        # Utilization
        if not isinstance(req.utilization, float):
            raise ValueError("Utilization must be a float.")
        if req.utilization < 0:
            raise ValueError("Utilization must be a positive float.")
        # Unique Periods
        if not isinstance(req.unique_periods, bool):
            raise ValueError("Unique Periods must be a boolean.")
        # Algorithm
        if req.algorithm is None:
            raise ValueError("Priority Assignment Algorithm must be provided." + algorithm_options)
        if req.algorithm is not None and not isinstance(req.algorithm, SchedulingAlgorithm):
            raise ValueError("Priority Assignment Algorithm must be a valid SchedulingAlgorithm." + algorithm_options)
        
    def __create_task(self, name: str, wcet: int, period: int) -> Task:
        '''
        Create a task with a given name, WCET, period, and deadline.

        Parameters:
            name (str): The name of the task.
            wcet (float): The worst-case execution time (WCET) of the task.
            period (int): The period of the task.

        Returns:
            Task: The created task.
        '''

        # BCET is 20% to 50% of WCET, ensuring it is at least 0
        bcet = round(max(0, wcet * random.uniform(0.2, 0.5)))
        return Task(
            name=name,
            bcet=bcet,
            wcet=wcet,
            period=period,
            deadline=period,  # Deadline equals period
        )
    
    def __create_taskset(self, utilization: list[float], periods: list[int]) -> TaskSet:
        '''
        Create a taskset based on the given utilization values and periods.

        Parameters:
            utilization (list[float]): The utilization values for the tasks.
            periods (list[int]): The periods for the tasks.

        Returns:
            TaskSet: The created taskset.
        '''
        
        taskset = TaskSet()
        for i, u in enumerate(utilization):
            wcet = max(1, round(periods[i] * u))
            task = self.__create_task(f"Task_{i}", wcet, periods[i])
            taskset.add_task(task)
        
        return taskset

    def __find_integer_n(self, x: float) -> int:
        '''
        Given a float x, find the smallest integer n such that n * x is an integer.

        Parameters:
            x (float): The input float x.

        Returns:
            int: The smallest integer n such that n * x is an integer.
        '''
        
        # Validate input
        if not isinstance(x, (float, int)):
            raise TypeError("Input must be a float or an integer.")
        if not (0 < x):
            raise ValueError("Input must be a positive float.")
        # Ensure x has at most 2 decimal places
        x = round(x, 2)

        # Convert x to a Fraction
        try:
            frac = Fraction(x).limit_denominator()
        except Exception as e:
            raise TypeError(f"Cannot convert input to a Fraction: {e}")

        n = frac.denominator
        
        # Verify that n * x is indeed an integer
        # Due to floating-point precision, use a tolerance
        product = n * x
        if not product.is_integer():
            # Alternatively, use a tolerance if necessary
            if not abs(product - round(product)) < 1e-10:
                raise ValueError("Unable to find an integer n such that n * x is exactly an integer.")

        return n