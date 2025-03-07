# Task Generator Documentation

## Overview

The Task Generator is a utility for creating real-time periodic task sets based on specified requirements. It's designed for testing and evaluating the simulator and RTA for the exercise by generating tasksets with specified utilization levels and periods constraints.

The tool is not able to generate schedulable / not schedulable tasksets, it only enforces utilization and period constraints, however:

**Some tasksets with known schedulability / non-schedulability are placed in the `test_examples` folder so you can better validate your RTA implementation**

## Configuration File Format

The generator uses a CSV configuration file (check examples in the `config.csv`) with the following columns:

| Column | Description |
|--------|-------------|
| Name | Identifier for the task set (string) |
| Size | Number of tasks in the set (integer) |
| Utilization | Target CPU utilization (float between 0-1) |
| UniquePeriods | Whether each task should have a unique period (true/false) |
| PriorityAssignment | Scheduling algorithm to use (currently only supports "RM" for Rate Monotonic) |

## Usage

To use the task generator, follow these steps:

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Plyncesilva/Taskset-Generator-Exercise.git
    cd Taskset-Generator
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    python -m pip install -r requirements.txt
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

### Running the tests

To run the test suite:

```bash
python -m pytest
```

### Output Directory

Task sets are stored in the `output_generated` directory by default, organized into subdirectories.
Each subdirectory further organizes task sets by utilization level.

### Unique Periods and Hyperperiod Considerations

- **Unique Periods**: When `UniquePeriods` is set to `true`, each task will have a unique period value. For large task sets, this can result in extremely large hyperperiods, which may impact analysis performance.

- **Non-Unique Periods**: When `UniquePeriods` is set to `false`, the generator optimizes for the smallest possible hyperperiod while still achieving the requested utilization. This option is recommended for large task sets or when simulation time is a concern.

Choose the period configuration based on your specific testing requirements and computational constraints.

### Contributing

Contributions to improve the task generator are welcome! If you encounter issues or have ideas for improvements