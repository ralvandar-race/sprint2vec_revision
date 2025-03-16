import torch
import torch.nn as nn
from sprint2vec.config import ExperimentConfig

class Sprint2Vec(nn.Module):
    def __init__(self, config: ExperimentConfig):
        super().__init__()
        self.config = config
        
        # Text Embedding Component
        self.text_encoder = nn.Sequential(
            nn.Linear(config.text_dim, config.hidden_size),
            nn.ReLU(),
            nn.Dropout(config.dropout)
        )
        
        # Validate bidirectional
        if not isinstance(config.bidirectional, bool):
            raise ValueError(f"Invalid bidirectional value: {config.bidirectional}. It must be a boolean.")
        
        # Developer Activity RNN
        valid_rnn_types = ['RNN', 'LSTM', 'GRU']
        if config.rnn_type not in valid_rnn_types:
            raise ValueError(f"Invalid rnn_type: {config.rnn_type}. Valid options are: {valid_rnn_types}")
        
        self.activity_rnn = getattr(nn, config.rnn_type)(
            input_size=config.activity_dim,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            dropout=config.dropout,
            bidirectional=config.bidirectional,
            batch_first=True
        )
        
        # Sprint Feature Encoder
        self.sprint_encoder = nn.Sequential(
            nn.Linear(config.sprint_dim, config.hidden_size),
            nn.ReLU(),
            nn.Dropout(config.dropout)
        )
        
        # Attention Layer
        if config.pooling_type == 'attention':
            self.attention = nn.Sequential(
                nn.Linear(config.hidden_size * (2 if config.bidirectional else 1), 1),
                nn.Softmax(dim=1)
            )
        
        # Feature Fusion Layer
        fusion_input_size = config.hidden_size * (3 if config.bidirectional else 2)
        self.fusion = nn.Sequential(
            nn.Linear(fusion_input_size, config.hidden_size),
            self.output = nn.Linear(config.hidden_size, config.num_output_classes)
        
        def forward(self, text_features, activity_features, sprint_features):
            # Text Embedding
            self.output = nn.Linear(config.hidden_size, 2)
        
        def forward(self, text_features, activity_features, sprint_features):
            """
            Forward pass for the Sprint2Vec model.
            
            Parameters:
            text_features (torch.Tensor): Tensor containing text features.
            activity_features (torch.Tensor): Tensor containing developer activity features.
            sprint_features (torch.Tensor): Tensor containing sprint features.
            
            Returns:
            torch.Tensor: Output tensor after passing through the model.
            """
            # Text Embedding
            text_embedded = self.text_encoder(text_features)
            
            # Developer Activity RNN
            activity_output, _ = self.activity_rnn(activity_features)
            
            # Sprint Feature Encoding
            sprint_embedded = self.sprint_encoder(sprint_features)
            
            # Attention Pooling
            if self.config.pooling_type == 'attention':
                attention_weights = self.attention(activity_output)
                activity_output = torch.sum(attention_weights * activity_output, dim=1)
            else:
                activity_output = torch.mean(activity_output, dim=1)
            
            # Feature Fusion
            fused_features = torch.cat((text_embedded, activity_output, sprint_embedded), dim=1)
            fused_output = self.fusion(fused_features)
            
            # Output Layer
            output = self.output(fused_output)
            
            return output
        return output
        self.output = nn.Linear(config.hidden_size, 2)
    
    def forward(self, text_features, activity_features, sprint_features):
        # Implementations as per paper Section 3...