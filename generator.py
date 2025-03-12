import sys
import os
import shutil

from generator import TaskRequirements, TaskGenerator

def parse_args():
    if len(sys.argv) < 2:
        print("Usage: python generator.py run --config <path_to_requirements.csv>")
        print("       python generator.py clean")
        sys.exit(1)
        
    command = sys.argv[1]
    # Get the base output directory from env var and remove any trailing slashes
    output_folder = f"output_generated"

    if command == "clean":
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            os.makedirs(output_folder)
            print(f"Cleaned all tasksets from {output_folder}")
        else:
            os.makedirs(output_folder)
            print(f"Created {output_folder} directory")
        sys.exit(0)
        
    elif command == "run":
        if len(sys.argv) != 4 or sys.argv[2] != "--config":
            print("Usage: python taskset_generator.py run --config <path_to_requirements.csv>")
            sys.exit(1)
        csv_path = sys.argv[3]
    else:
        print("Unknown command. Use 'run' or 'clean'")
        sys.exit(1)
    return csv_path, output_folder

if __name__ == '__main__':
    csv_path, output_folder = parse_args()

    requirements = TaskRequirements.from_csv(csv_path)

    generator = TaskGenerator(requirements, output_folder)
    
    generator.generate_tasksets()