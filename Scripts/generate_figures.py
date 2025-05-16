import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def generate_paper_figures():
    results_path = Path("Results")
    
    # Figure 1: Performance Comparison
    df = pd.read_csv(results_path / "performance_metrics.csv")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Repository', y='Performance')
    plt.title('Sprint Performance Prediction')
    plt.savefig(results_path / 'figure1.png')
    
    # Figure 2: Feature Importance
    feature_importance = pd.read_csv(results_path / "feature_importance.csv")
    plt.figure(figsize=(12, 6))
    sns.heatmap(feature_importance, annot=True)
    plt.title('Feature Importance Analysis')
    plt.savefig(results_path / 'figure2.png')