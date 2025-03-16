import torch
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from TrainActRNN import DeveloperActivityRNN
from dataset import SprintDataset
from config import ModelConfig
from torch.utils.data import DataLoader

def evaluate_model(repo_name):
    config = ModelConfig()
    
    # Load test data
    test_path = Path(f"D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing/{repo_name}_processed_test.csv.gz")
    test_df = pd.read_csv(test_path, compression='gzip')
    test_dataset = SprintDataset(test_df, config)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Load trained model
    model_path = Path(f"D:/REVA/Capstone1/sprint2vec_revision/Models/{repo_name}_lstm_model.pt")
    model = DeveloperActivityRNN(input_size=5, config=config)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    predictions = []
    actuals = []
    
    with torch.no_grad():
        for batch in test_loader:
            features = batch['features']
            targets = batch['target']
            outputs = model(features)
            
            predictions.extend(outputs.numpy())
            actuals.extend(targets.numpy())
    
    # Convert to numpy arrays
    predictions = pd.DataFrame(predictions, columns=['pred_productivity', 'pred_quality'])
    actuals = pd.DataFrame(actuals, columns=['actual_productivity', 'actual_quality'])
    
    # Calculate metrics
    mse = ((predictions - actuals) ** 2).mean()
    print(f"\nMean Squared Error:")
    print(f"Productivity: {mse['pred_productivity']:.4f}")
    print(f"Quality: {mse['pred_quality']:.4f}")
    
    # Plot results
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.scatter(actuals['actual_productivity'], predictions['pred_productivity'])
    plt.plot([0, 1], [0, 1], 'r--')
    plt.title('Productivity Predictions')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    
    plt.subplot(1, 2, 2)
    plt.scatter(actuals['actual_quality'], predictions['pred_quality'])
    plt.plot([0, 1], [0, 1], 'r--')
    plt.title('Quality Predictions')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    
    plt.tight_layout()
    plt.savefig(f'D:/REVA/Capstone1/sprint2vec_revision/Results/{repo_name}_predictions.png')
    plt.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python evaluate_model.py <repository_name>")
        sys.exit(1)
    
    evaluate_model(sys.argv[1].lower())