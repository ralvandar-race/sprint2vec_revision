import sys
import os
import pandas as pd

class DBConfig():
    def __init__(self, host, port, user, pwd, repo, folder):
        self.host = host
        self.port = int(port)
        self.user = user
        self.pwd = pwd
        self.repo = repo
        self.folder = self._find_data_folder(folder)
        self._verify_data_folder()

    def _find_data_folder(self, folder):
        """Find the correct data folder"""
        possible_paths = [
            folder,
            os.path.join(folder, "existing"),
            os.path.join(folder, "sprint2vec"),
            os.path.join(folder, f"{self.repo.name}")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Check if the folder contains the expected data files
                expected_files = [
                    f"{self.repo.name}_existing_train.csv.gz",
                    f"{self.repo.name}_existing_test.csv.gz",
                    f"{self.repo.name}_existing_valid.csv.gz"
                ]
                if any(os.path.exists(os.path.join(path, f)) for f in expected_files):
                    print(f"Found data folder with required files: {path}")
                    return path
                
        print("Warning: No valid data folder found with required files.")
        return folder

    def _verify_data_folder(self):
        """Verify and print data folder structure"""
        print(f"\nChecking data folder: {self.folder}")
        if os.path.exists(self.folder):
            print("Available files:")
            files = [f for f in os.listdir(self.folder) 
                    if f.startswith(self.repo.name) and f.endswith('.csv.gz')]
            for f in files:
                print(f"    {f}")
                
            # Load a sample to verify data structure
            if files:
                sample_file = os.path.join(self.folder, files[0])
                try:
                    df = pd.read_csv(sample_file, compression='gzip', nrows=1)
                    print(f"\nData columns available: {', '.join(df.columns)}")
                except Exception as e:
                    print(f"Warning: Could not read sample data: {e}")
        else:
            print(f"Warning: Folder not found: {self.folder}")

def createDB(repo, host="localhost", port=3306, user="root", pwd="capstone", 
             folder="D:/REVA/Capstone1/sprint2vec_revision/Dataset"):
    """
    Create a new DBConfig object with existing dataset
    Args:
        repo: Repository configuration object
        host: Database host
        port: Database port
        user: Database user
        pwd: Database password
        folder: Path to the folder containing dataset
    Returns:
        DBConfig object
    """
    return DBConfig(host, port, user, pwd, repo, folder)


