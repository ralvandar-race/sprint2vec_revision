import torch
import torch.nn as nn

class Sprint2Vec(nn.Module):
    def __init__(self, feature_dims, hidden_dim=128, dropout=0.2):
        super().__init__()
        
        # Store dimensions
        self.text_dim = feature_dims['text_dim']
        self.activity_dim = feature_dims['activity_dim']
        self.sprint_dim = feature_dims['sprint_dim']
        self.seq_length = feature_dims.get('seq_length', 10)
        
        # Text Encoder
        self.text_encoder = nn.Sequential(
            nn.Linear(self.text_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Activity LSTM
        self.activity_lstm = nn.LSTM(
            input_size=self.activity_dim,
            hidden_size=hidden_dim,
            batch_first=True
        )
        
        # Sprint Encoder
        self.sprint_encoder = nn.Sequential(
            nn.Linear(self.sprint_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Fusion Layer
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 2)  # 2 outputs: productivity, quality
        )
    
    def forward(self, text, activity, sprint):
        # Reshape activity input to (batch, seq_length, features)
        if activity.dim() == 2:
            batch_size = activity.size(0)
            activity = activity.unsqueeze(1).expand(-1, self.seq_length, -1)
        
        # Process features
        text_features = self.text_encoder(text)
        activity_output, _ = self.activity_lstm(activity)
        activity_features = activity_output[:, -1, :]  # Take last timestep
        sprint_features = self.sprint_encoder(sprint)
        
        # Combine features
        combined = torch.cat([text_features, activity_features, sprint_features], dim=1)
        return self.fusion(combined)