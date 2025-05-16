from dataclasses import dataclass
import torch
from pathlib import Path

@dataclass
class ExperimentConfig:
    # Model Architecture (from paper Section 3)
    embedding_dim: int = 100
    hidden_size: int = 128
    num_layers: int = 2
    dropout: float = 0.2
    
    # Feature Dimensions (from paper Section 3.2)
    text_dim: int = 100
    activity_dim: int = 64
    sprint_dim: int = 5
    
    # Training Parameters (from paper Section 4)
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 50
    weight_decay: float = 1e-5  # L2 regularization
    
    # Data Parameters
    max_sequence_length: int = 100
    num_workers: int = 4
    validation_split: float = 0.2
    
    # Device Configuration
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Model Specific Parameters
    rnn_type: str = 'LSTM'  # Options: LSTM, GRU
    bidirectional: bool = True
    pooling_type: str = 'attention'  # Options: max, mean, attention
    
    # Early Stopping Parameters
    patience: int = 5
    min_delta: float = 1e-4

@dataclass
class ProjectConfig:
    # Paths
    base_path: Path = Path("D:/REVA/Capstone1/sprint2vec_revision")
    dataset_path: Path = base_path / "Dataset"
    models_path: Path = base_path / "Models"
    results_path: Path = base_path / "Results"
    
    # Repositories
    repositories: list = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
    
    # Model parameters
    embedding_dim: int = 100
    hidden_size: int = 128
    dropout: float = 0.2