import pandas as pd
from pathlib import Path

class DatasetLoader:
    def __init__(self):
        self.base_path = Path("D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing")
        self.repositories = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
    
    def load_repository_data(self, repo_name, split='train'):
        """Load repository data from existing dataset"""
        if repo_name not in self.repositories:
            raise ValueError(f"Unknown repository: {repo_name}")
        
        file_path = self.base_path / f"{repo_name}_existing_{split}.csv.gz"
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
            
        return pd.read_csv(file_path, compression='gzip')
    
    def get_splits(self, repo_name):
        """Get all splits (train/test/valid) for a repository"""
        return {
            split: self.load_repository_data(repo_name, split)
            for split in ['train', 'test', 'valid']
        }