from dataclasses import dataclass
import torch

@dataclass
class ModelConfig:
    # System Configuration
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    num_workers: int = 0  # For Windows, use 0 to avoid multiprocessing issues
    
    # Model Parameters
    rnn_type: str = 'lstm'
    hidden_dim: int = 16
    num_layers: int = 2
    dropout: float = 0.2
    
    # Training Parameters
    batch_size: int = 32
    epochs: int = 10
    learning_rate: float = 0.001
    weight_decay: float = 1e-5
    
    # Data Parameters
    text_type: str = 'bow'
    dev_activity_type: str = 'full'
    pooling_type: str = 'mean'
    
    def __post_init__(self):
        print(f"Using device: {self.device}")