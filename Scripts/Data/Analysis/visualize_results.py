import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

class ResultsVisualizer:
    def __init__(self, base_path: str = "Results"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def plot_training_curves(self, train_losses, val_losses, repo_name):
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='Training Loss')
        plt.plot(val_losses, label='Validation Loss')
        plt.title(f'Training Progress - {repo_name}')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(self.base_path / f'{repo_name}_training_curves.png')
        plt.close()
    
    def plot_model_predictions(self, actuals, predictions, repo_name):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Productivity predictions
        sns.scatterplot(x=actuals[:, 0], y=predictions[:, 0], ax=ax1)
        ax1.set_title(f'{repo_name} - Productivity')
        ax1.set_xlabel('Actual')
        ax1.set_ylabel('Predicted')
        
        # Quality predictions
        sns.scatterplot(x=actuals[:, 1], y=predictions[:, 1], ax=ax2)
        ax2.set_title(f'{repo_name} - Quality')
        ax2.set_xlabel('Actual')
        ax2.set_ylabel('Predicted')
        
        plt.tight_layout()
        plt.savefig(self.base_path / f'{repo_name}_predictions.png')
        plt.close()
    
    def plot_repository_comparison(self, results):
        df = pd.DataFrame(results).T
        metrics = ['productivity_mae', 'quality_mae']
        
        plt.figure(figsize=(12, 6))
        df[metrics].plot(kind='bar', width=0.8)
        plt.title('Performance Comparison Across Repositories')
        plt.xlabel('Repository')
        plt.ylabel('Mean Absolute Error')
        plt.legend(['Productivity', 'Quality'])
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.base_path / 'repository_comparison.png')
        plt.close()