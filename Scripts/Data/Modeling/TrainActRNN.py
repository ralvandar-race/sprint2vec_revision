import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
import pandas as pd
import sys
from config import ModelConfig
from dataset import SprintDataset

class DeveloperActivityRNN(nn.Module):
    def __init__(self, input_size, config):
        super().__init__()
        self.config = config
        
        # input_size is the number of features (5 in your case)
        self.rnn = getattr(nn, config.rnn_type.upper())(
            input_size=input_size,  # This should match the feature dimension
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            dropout=config.dropout,
            batch_first=True
        )
        
        self.fc = nn.Linear(config.hidden_dim, 2)
    
    def forward(self, x):
        # x shape: [batch_size, sequence_length, feature_size]
        output, _ = self.rnn(x)
        
        if self.config.pooling_type == 'mean':
            output = torch.mean(output, dim=1)
        else:
            output = output[:, -1, :]
            
        return self.fc(output)

def train_model(model, train_loader, config):
    model = model.to(config.device)
    optimizer = torch.optim.Adam(
        model.parameters(), 
        lr=config.learning_rate
    )
    criterion = nn.MSELoss()
    
    for epoch in range(config.epochs):
        model.train()
        total_loss = 0
        
        for batch_idx, batch in enumerate(train_loader):
            features = batch['features'].to(config.device)
            targets = batch['target'].to(config.device)
            
            # Debug shapes
            if batch_idx == 0:
                print(f"\nInput shapes:")
                print(f"Features: {features.shape}")
                print(f"Targets: {targets.shape}")
            
            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, targets)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}/{config.epochs}, Loss: {avg_loss:.4f}")

def main(repo_name):
    try:
        config = ModelConfig()
        
        # Load data
        data_path = Path(f"D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing/{repo_name}_processed_train.csv.gz")
        if not data_path.exists():
            print(f"Error: Data file not found at {data_path}")
            return
            
        df = pd.read_csv(data_path, compression='gzip')
        dataset = SprintDataset(df, config)
        
        # Get the actual feature size from the dataset
        _, _, feature_size = dataset.features.shape
        print(f"Feature size: {feature_size}")
        
        # Initialize model with correct input size
        model = DeveloperActivityRNN(input_size=feature_size, config=config)
        
        train_loader = DataLoader(
            dataset, 
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_workers
        )
        
        # Train model
        print(f"Training {config.rnn_type.upper()} model for {repo_name}")
        train_model(model, train_loader, config)
        
        # Save model
        model_path = Path(f"D:/REVA/Capstone1/sprint2vec_revision/Models/{repo_name}_{config.rnn_type}_model.pt")
        torch.save(model.state_dict(), model_path)
        print(f"Model saved to {model_path}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python TrainActRNN.py <repository_name>")
        sys.exit(1)
    
    main(sys.argv[1].lower())