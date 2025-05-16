import json
import os
import pandas as pd

def loadRapidBoardJSON(repo_name, data_folder):
    """
    Load the board data from existing CSV files
    Args:
        repo_name: Name of the repository (e.g., 'apache')
        data_folder: Path to the data folder
    Returns:
        Dictionary with board data in JSON format
    """
    train_file = os.path.join(data_folder, f"{repo_name}_existing_train.csv.gz")
    
    if os.path.exists(train_file):
        print(f"Loading training data from: {train_file}")
        df = pd.read_csv(train_file, compression='gzip')
        print(f"Available columns: {', '.join(df.columns)}")
        
        # Create unique string IDs for each record
        views = [{'id': f"{repo_name}_record_{i}"} for i in range(len(df))]
        return {'views': views}
    else:
        raise FileNotFoundError(f"Training data file not found: {train_file}")

def loadBoardJSON(board_id, repo_name, data_folder):
    """
    Load board details from CSV files
    Args:
        board_id: Board ID to load
        repo_name: Name of the repository
        data_folder: Path to the data folder
    Returns:
        Dictionary with board details
    """
    train_file = os.path.join(data_folder, f"{repo_name}_existing_train.csv.gz")
    
    if os.path.exists(train_file):
        print(f"Loading board data from: {train_file}")
        df = pd.read_csv(train_file, compression='gzip')
        board_data = df[df['board_id'] == board_id].to_dict('records')
        return board_data[0] if board_data else {}
    else:
        raise FileNotFoundError(f"Board data file not found: {train_file}")