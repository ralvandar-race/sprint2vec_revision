import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np

class SprintDataset(Dataset):
    def __init__(self, df, config, sequence_length=10):
        self.data = df
        self.config = config
        self.sequence_length = sequence_length
        
        # Extract features
        feature_cols = [
            'plan_duration', 'no_issue', 'no_teammember',
            'no_component_mean', 'fog_index_mean'
        ]
        
        # Shape features: [num_samples, num_features]
        features = df[feature_cols].values
        
        # Reshape to [num_samples, sequence_length, num_features]
        self.features = torch.FloatTensor(features).unsqueeze(1).repeat(1, sequence_length, 1)
        
        # Extract targets
        self.targets = torch.FloatTensor(
            df[['productivity', 'quality_impact']].values
        )
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'target': self.targets[idx]
        }