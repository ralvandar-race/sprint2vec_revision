import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import torch
import pandas as pd
from tqdm import tqdm

from sprint2vec.config import ExperimentConfig
from sprint2vec.Models.Sprint2Vec import Sprint2Vec
from Data.dataset import SprintDataset
from Training.train_model import train_sprint2vec
from Data.Analysis.analyze_results import ResultsAnalyzer

def run_pipeline(repo_name: str):
    """Run complete Sprint2Vec pipeline for a repository"""
    print(f"\nProcessing {repo_name.upper()}")
    print("-" * 50)
    
    # Setup paths
    base_path = Path("D:/REVA/Capstone1/sprint2vec_revision")
    data_path = base_path / "Dataset/existing"
    results_path = base_path / "Results" / repo_name
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    config = ExperimentConfig()
    
    # Load datasets
    print("\nLoading datasets...")
    train_data = SprintDataset(
        pd.read_csv(data_path / f"{repo_name}_existing_train.csv.gz"),
        config
    )
    val_data = SprintDataset(
        pd.read_csv(data_path / f"{repo_name}_existing_valid.csv.gz"),
        config
    )
    test_data = SprintDataset(
        pd.read_csv(data_path / f"{repo_name}_existing_test.csv.gz"),
        config
    )
    
    # Create data loaders
    train_loader = torch.utils.data.DataLoader(
        train_data,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers
    )
    val_loader = torch.utils.data.DataLoader(
        val_data,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers
    )
    test_loader = torch.utils.data.DataLoader(
        test_data,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers
    )
    
    # Initialize model
    print("\nInitializing model...")
    model = Sprint2Vec(config)
    
    # Train model
    print("\nStarting training...")
    train_sprint2vec(model, train_loader, val_loader, config, repo_name)
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    model.load_state_dict(torch.load(results_path / 'best_model.pt'))
    model.eval()
    
    test_predictions = []
    test_actuals = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc='Testing'):
            text_features = batch['text_features'].to(config.device)
            activity_features = batch['activity_features'].to(config.device)
            sprint_features = batch['sprint_features'].to(config.device)
            
            outputs = model(text_features, activity_features, sprint_features)
            test_predictions.extend(outputs.cpu().numpy())
            test_actuals.extend(batch['targets'].numpy())
    
    # Save test results
    test_results = pd.DataFrame({
        'actual_productivity': [x[0] for x in test_actuals],
        'actual_quality': [x[1] for x in test_actuals],
        'predicted_productivity': [x[0] for x in test_predictions],
        'predicted_quality': [x[1] for x in test_predictions]
    })
    test_results.to_csv(results_path / 'test_predictions.csv', index=False)
    
    # Analyze results
    analyzer = ResultsAnalyzer()
    analyzer.plot_comparison()
    
    print(f"\nPipeline completed for {repo_name}")
    print("Results saved in:", results_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_complete_pipeline.py <repository_name>")
        sys.exit(1)
    
    repo_name = sys.argv[1].lower()
    valid_repos = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
    
    if repo_name not in valid_repos:
        print(f"Error: Repository must be one of {valid_repos}")
        sys.exit(1)
    
    run_pipeline(repo_name)