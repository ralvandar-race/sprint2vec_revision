import pandas as pd
import numpy as np

class FeatureExtractor:
    def __init__(self, data_path):
        self.data_path = data_path
    
    def load_dataset(self, repo_name, split='train'):
        """Load repository dataset"""
        file_path = f"{self.data_path}/{repo_name}_existing_{split}.csv.gz"
        return pd.read_csv(file_path, compression='gzip')