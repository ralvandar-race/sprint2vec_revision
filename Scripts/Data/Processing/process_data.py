import torch
from torch.utils.data import Dataset, DataLoader
import mysql.connector
import pandas as pd
import numpy as np
from pathlib import Path
import logging

class SprintDataset(Dataset):
    def __init__(self, features, targets, seq_length=10):
        self.text_features = torch.FloatTensor(features['text'])
        self.activity_features = torch.FloatTensor(features['activity'])
        self.sprint_features = torch.FloatTensor(features['sprint'])
        self.targets = torch.FloatTensor(targets)
        self.seq_length = seq_length
    
    def __len__(self):
        return len(self.targets)
    
    def __getitem__(self, idx):
        # Reshape activity features to (seq_length, features)
        activity = self.activity_features[idx].repeat(self.seq_length, 1)
        
        return {
            'text': self.text_features[idx],
            'activity': activity,
            'sprint': self.sprint_features[idx],
            'targets': self.targets[idx]
        }

class DataProcessor:
    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.seq_length = 10  # Number of timesteps for activity sequence
        self.conn_params = {
            'host': 'localhost',
            'user': 'root',
            'password': 'capstone',
            'database': 'sprint2vec'
        }
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def get_data_loaders(self, batch_size: int = 32):
        try:
            conn = mysql.connector.connect(**self.conn_params)
            query = """
                SELECT 
                    s.sprint_id,
                    s.plan_duration,
                    s.no_issue,
                    s.no_teammember,
                    s.productivity,
                    s.quality_impact,
                    AVG(COALESCE(i.fog_index, 0)) as avg_fog_index,
                    COUNT(DISTINCT da.activity_type) as activity_count
                FROM sprints s
                LEFT JOIN issues i ON s.sprint_id = i.sprint_id
                LEFT JOIN developer_activities da ON s.sprint_id = da.sprint_id
                WHERE s.repository = %s
                GROUP BY 
                    s.sprint_id,
                    s.plan_duration,
                    s.no_issue,
                    s.no_teammember,
                    s.productivity,
                    s.quality_impact
            """
            
            df = pd.read_sql(query, conn, params=(self.repo_name,))
            conn.close()
            
            if df.empty:
                raise ValueError(f"No data found for repository: {self.repo_name}")
            
            # Convert to float32 and handle missing values
            df = df.fillna(0).astype(np.float32)
            
            # Process features and targets
            features = self._extract_features(df)
            targets = df[['productivity', 'quality_impact']].values
            
            # Split data
            train_size = int(0.7 * len(df))
            val_size = int(0.15 * len(df))
            
            datasets = self._create_datasets(features, targets, train_size, val_size)
            return self._create_dataloaders(datasets, batch_size)
            
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            raise
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            raise
    
    def _extract_features(self, df):
        """Extract and reshape features for Sprint2Vec"""
        text_features = df[['avg_fog_index']].values
        activity_features = df[['activity_count']].values
        sprint_features = df[['plan_duration', 'no_issue', 'no_teammember']].values
        
        return {
            'text': text_features,
            'activity': activity_features,
            'sprint': sprint_features
        }
    
    def _create_datasets(self, features, targets, train_size, val_size):
        train_features = {k: v[:train_size] for k, v in features.items()}
        val_features = {k: v[train_size:train_size+val_size] for k, v in features.items()}
        test_features = {k: v[train_size+val_size:] for k, v in features.items()}
        
        train_targets = targets[:train_size]
        val_targets = targets[train_size:train_size+val_size]
        test_targets = targets[train_size+val_size:]
        
        return {
            'train': (train_features, train_targets),
            'val': (val_features, val_targets),
            'test': (test_features, test_targets)
        }
    
    def _create_dataloaders(self, datasets, batch_size):
        return (
            DataLoader(SprintDataset(*datasets['train']), batch_size=batch_size, shuffle=True),
            DataLoader(SprintDataset(*datasets['val']), batch_size=batch_size),
            DataLoader(SprintDataset(*datasets['test']), batch_size=batch_size)
        )
    
    def get_feature_dimensions(self):
        return {
            'text_dim': 1,  # fog_index
            'activity_dim': 1,  # activity_count
            'sprint_dim': 3,  # plan_duration, no_issue, no_teammember
            'seq_length': self.seq_length
        }