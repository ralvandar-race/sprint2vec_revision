import torch
from torch.utils.data import DataLoader
from pathlib import Path
import pandas as pd
from tqdm import tqdm

def train_sprint2vec(model, train_loader, val_loader, config, repo_name):
    """Train Sprint2Vec model"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    criterion = nn.MSELoss()
    
    best_val_loss = float('inf')
    results_path = Path(f"D:/REVA/Capstone1/sprint2vec_revision/Results/{repo_name}")
    results_path.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(config.epochs):
        # Training
        model.train()
        train_loss = 0
        for batch in tqdm(train_loader, desc=f'Epoch {epoch+1}/{config.epochs}'):
            optimizer.zero_grad()
            
            text_features = batch['text_features'].to(device)
            activity_features = batch['activity_features'].to(device)
            sprint_features = batch['sprint_features'].to(device)
            targets = batch['targets'].to(device)
            
            outputs = model(text_features, activity_features, sprint_features)
            loss = criterion(outputs, targets)
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        predictions = []
        actuals = []
        
        with torch.no_grad():
            for batch in val_loader:
                text_features = batch['text_features'].to(device)
                activity_features = batch['activity_features'].to(device)
                sprint_features = batch['sprint_features'].to(device)
                targets = batch['targets'].to(device)
                
                outputs = model(text_features, activity_features, sprint_features)
                val_loss += criterion(outputs, targets).item()
                
                predictions.extend(outputs.cpu().numpy())
                actuals.extend(targets.cpu().numpy())
        
        # Save results
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        
        print(f'Epoch {epoch+1}: Train Loss = {avg_train_loss:.4f}, Val Loss = {avg_val_loss:.4f}')
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), results_path / 'best_model.pt')
            
            # Save predictions
            results_df = pd.DataFrame({
                'actual_productivity': [x[0] for x in actuals],
                'actual_quality': [x[1] for x in actuals],
                'predicted_productivity': [x[0] for x in predictions],
                'predicted_quality': [x[1] for x in predictions]
            })
            results_df.to_csv(results_path / 'predictions.csv', index=False)