from dataclasses import dataclass

@dataclass
class Sprint2VecConfig:
    # Model Architecture
    text_dim: int = 100
    activity_dim: int = 64
    sprint_dim: int = 5
    hidden_dim: int = 128
    num_layers: int = 2
    dropout: float = 0.2
    
    # Training Parameters
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 50
    
    # Data Parameters
    max_sequence_length: int = 100