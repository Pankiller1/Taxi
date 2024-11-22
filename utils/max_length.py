import pandas as pd
import ast

if __name__ == "__main__":
    # Load the CSV file
    file_path = "../data/results.csv"  # Replace with your actual file path
    data = pd.read_csv(file_path)

    # Parse the trajectory column as a list
    data['trajectory'] = data['trajectory'].apply(ast.literal_eval)

    # Calculate the maximum length of trajectory points
    max_trajectory_length = data['trajectory'].apply(len).max()

    print("Maximum length of trajectory points:", max_trajectory_length)
