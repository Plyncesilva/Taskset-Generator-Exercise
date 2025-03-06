# Task Generator Documentation

## Overview

The Task Generator is a utility for creating real-time periodic task sets based on specified requirements. It's designed for testing and evaluating the simulator and RTA for the exercise by generating tasks with utilization levels and periods constraints.

## Key Components

- **TaskGenerator**: Main class that generates task sets based on requirements
- **TaskRequirements**: Contains specifications for the task sets to be generated
- **Requirement**: Individual specification for a single task set

## Configuration File Format

The generator uses a CSV configuration file with the following columns:

| Column | Description |
|--------|-------------|
| Name | Identifier for the task set (string) |
| Size | Number of tasks in the set (integer) |
| Utilization | Target CPU utilization (float between 0-1) |
| UniquePeriods | Whether each task should have a unique period (true/false) |
| PriorityAssignment | Scheduling algorithm to use (currently only supports "RM" for Rate Monotonic) |

### Example Configuration:
```csv
Name,Size,Utilization,UniquePeriods,PriorityAssignment
Example_Low_Utilization,5,0.2,true,RM
Example_Medium_Utilization,8,0.5,false,RM
Example_High_Utilization,12,0.8,true,RM
Example_Full_Utilization,10,1.0,false,RM
Example_Overutilization,6,1.2,false,RM
```

This configuration generates 5 different task sets, ranging from low utilization to overutilization systems.

## Usage

To use the task generator, follow these steps:

### Installation

1. Clone the repository and submodules:
    ```bash
    git clone https://github.com/Plyncesilva/Taskset-Generator.git
    cd Taskset-Generator
    ```

### Running the Generator

Execute the generator from the command line with example configurations:

```bash
python generator.py run --config config.csv
```

The generator will create task sets based on the specifications in your configuration file.

### Cleaning Generated Task Sets

To remove previously generated task sets:

```bash
python generator.py clean
```

### Output Directory

Task sets are stored in the `tests/generated` directory by default, organized into subdirectories:
- `schedulable` - Contains task sets that are schedulable
- `not_schedulable` - Contains task sets that are unschedulable

Each subdirectory further organizes task sets by utilization level.

### Unique Periods and Hyperperiod Considerations

- **Unique Periods**: When `UniquePeriods` is set to `true`, each task will have a unique period value. For large task sets, this can result in extremely large hyperperiods, which may impact analysis performance.

- **Non-Unique Periods**: When `UniquePeriods` is set to `false`, the generator optimizes for the smallest possible hyperperiod while still achieving the requested utilization. This option is recommended for large task sets or when simulation time is a concern.

Choose the period configuration based on your specific testing requirements and computational constraints.

### Contributing

Contributions to improve the task generator are welcome! If you encounter issues or have ideas for improvements