import pandas as pd
import os
from pathlib import Path

def load_repository_data(repo_name, data_folder="existing"):
    """
    Load repository data from CSV files
    Args:
        repo_name: Name of repository (e.g., 'apache')
        data_folder: Dataset folder name (default: 'existing')
    Returns:
        dict: Dictionary containing train, test, validation DataFrames
    """
    base_path = Path("D:/REVA/Capstone1/sprint2vec_revision/Dataset") / data_folder
    data = {}
    
    for split in ['train', 'test', 'valid']:
        file_path = base_path / f"{repo_name}_{data_folder}_{split}.csv.gz"
        print(f"Loading {split} data from: {file_path}")
        data[split] = pd.read_csv(file_path, compression='gzip')
        
    return data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python LoadData.py <repository_name>")
        sys.exit(1)
        
    repo_name = sys.argv[1].lower()
    data = load_repository_data(repo_name)
    
    # Print summary statistics
    for split, df in data.items():
        print(f"\n{split.upper()} Dataset Summary:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {', '.join(df.columns)}")