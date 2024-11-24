# A script to convert original trajectory into tokens
import pandas as pd
import csv

def process_trajectory(trajectory, max_length=2048):
    """
    Process the trajectory by transforming coordinates relative to a center point,
    adding beginning and ending tokens, and padding to the desired length.

    Args:
        trajectory (list): List of [x, y] points in the trajectory.
        max_length (int): Desired maximum length of the processed trajectory.

    Returns:
        list: Processed trajectory with tokens and padding.
    """
    center = [114.085947, 22.547]
    start_token = [-20, -20, -1]
    end_token = [20, 20, -2]
    padding_token = [0, 0, 0]
    
    # Transform trajectory points relative to the center
    transformed_traj = [[point[0], point[1], i+1] for i, point in enumerate(trajectory)]
    
    # Add start and end tokens
    processed_traj = [start_token] + transformed_traj + [end_token]
    
    # Pad or truncate to the max length
    if len(processed_traj) < max_length:
        processed_traj.extend([padding_token] * (max_length - len(processed_traj)))
    else:
        print("Warning: Max length is not correct.")
        processed_traj = processed_traj[:max_length]
    
    return processed_traj


if __name__ == "__main__":
    file_path = "../data/results.csv"  # Replace with your actual file path
    output_path = "../data/token_traj.csv"

    # Open input and output files
    with open(file_path, "r") as infile, open(output_path, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ["processed_trajectory", "time_elapsed"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # Parse trajectory as a Python list
            trajectory = eval(row["trajectory"])  # Convert string to list safely
            
            # Process the trajectory
            processed_trajectory = process_trajectory(trajectory)

            # Write processed data to the output file
            writer.writerow({
                "processed_trajectory": processed_trajectory,
                "time_elapsed": row["time_elapsed"]
            })

    print(f"Processed data saved to {output_path}")
