import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

class ResultsAnalyzer:
    def __init__(self):
        self.results_dir = Path("D:/REVA/Capstone1/sprint2vec_revision/Results")
        self.repositories = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
        
        # Paper results from Table 3
        self.paper_results = pd.DataFrame({
            'Repository': self.repositories,
            'Productivity_MAE_Paper': [0.15, 0.14, 0.16, 0.15, 0.14],
            'Quality_MAE_Paper': [0.12, 0.11, 0.13, 0.12, 0.11]
        })
        
    def load_repository_results(self, repo_name):
        """Load results for a specific repository"""
        metrics_file = self.results_dir / f"{repo_name}_test_metrics.csv"
        if metrics_file.exists():
            return pd.read_csv(metrics_file)
        return None
    
    def compare_with_paper_results(self):
        """Compare results with paper benchmarks (Table 3)"""
        comparison = []
        for repo in self.repositories:
            results = self.load_repository_results(repo)
            if results is not None:
                paper = self.paper_results[self.paper_results['Repository'] == repo].iloc[0]
                comparison.append({
                    'Repository': repo,
                    'Productivity_MAE_Paper': paper['Productivity_MAE_Paper'],
                    'Productivity_MAE_Ours': results['productivity_mae'].iloc[0],
                    'Quality_MAE_Paper': paper['Quality_MAE_Paper'],
                    'Quality_MAE_Ours': results['quality_mae'].iloc[0]
                })
        
        return pd.DataFrame(comparison)
    
    def plot_comparison(self):
        """Plot comparison between paper and our results"""
        comparison = self.compare_with_paper_results()
        
        plt.figure(figsize=(12, 6))
        
        # Productivity comparison
        plt.subplot(1, 2, 1)
        sns.barplot(data=comparison.melt(id_vars='Repository', 
                                       value_vars=['Productivity_MAE_Paper', 'Productivity_MAE_Ours']),
                   x='Repository', y='value', hue='variable')
        plt.title('Productivity MAE Comparison')
        plt.xticks(rotation=45)
        
        # Quality comparison
        plt.subplot(1, 2, 2)
        sns.barplot(data=comparison.melt(id_vars='Repository',
                                       value_vars=['Quality_MAE_Paper', 'Quality_MAE_Ours']),
                   x='Repository', y='value', hue='variable')
        plt.title('Quality MAE Comparison')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'comparison_with_paper.png')
        plt.close()

def analyze_predictions(actual, predicted, repo_name):
    """Analyze model predictions"""
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    # Plot results
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=actual, y=predicted)
    plt.title(f'Predictions vs Actuals - {repo_name}')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.savefig(f'Results/{repo_name}_predictions.png')

if __name__ == "__main__":
    analyzer = ResultsAnalyzer()
    comparison = analyzer.compare_with_paper_results()
    print("\nComparison with Paper Results:")
    print(comparison.to_string(index=False))
    analyzer.plot_comparison()