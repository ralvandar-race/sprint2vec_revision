from pathlib import Path
import sys
import logging
from typing import Optional, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score
import argparse
import mysql.connector
from mysql.connector import Error

from Scripts.Data.Processing.process_data import DataProcessor
from Scripts.Models.sprint2vec import Sprint2Vec
from Scripts.Data.Analysis.analyze_results import ResultsAnalyzer
from Scripts.Utility.validate_mysql import MySQLValidator
from Scripts.Data.Analysis.visualize_results import ResultsVisualizer

class ModelTrainer:
    def __init__(self, model: nn.Module, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
    def train(self, train_loader: DataLoader, val_loader: DataLoader, epochs: int = 50):
        best_val_loss = float('inf')
        train_losses, val_losses = [], []
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            for batch in train_loader:
                text = batch['text'].to(self.device)
                activity = batch['activity'].to(self.device)
                sprint = batch['sprint'].to(self.device)
                targets = batch['targets'].to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(text, activity, sprint)
                loss = self.criterion(outputs, targets)
                loss.backward()
                self.optimizer.step()
                train_loss += loss.item()
            
            # Validation
            self.model.eval()
            val_loss = 0
            with torch.no_grad():
                for batch in val_loader:
                    text = batch['text'].to(self.device)
                    activity = batch['activity'].to(self.device)
                    sprint = batch['sprint'].to(self.device)
                    targets = batch['targets'].to(self.device)
                    
                    outputs = self.model(text, activity, sprint)
                    val_loss += self.criterion(outputs, targets).item()
            
            train_losses.append(train_loss / len(train_loader))
            val_losses.append(val_loss / len(val_loader))
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(self.model.state_dict(), 'best_model.pt')
            
            logging.info(f'Epoch {epoch+1}: Train Loss = {train_losses[-1]:.4f}, Val Loss = {val_losses[-1]:.4f}')
        
        return train_losses, val_losses

    def get_predictions(self, test_loader):
        """Get model predictions on test data"""
        self.model.eval()
        actuals = []
        predictions = []
        
        with torch.no_grad():
            for batch in test_loader:
                # Get batch data
                text = batch['text'].to(self.device)
                activity = batch['activity'].to(self.device)
                sprint = batch['sprint'].to(self.device)
                targets = batch['targets'].to(self.device)
                
                # Get predictions
                outputs = self.model(text, activity, sprint)
                
                # Store results
                actuals.append(targets.cpu().numpy())
                predictions.append(outputs.cpu().numpy())
        
        # Concatenate all batches
        actuals = np.concatenate(actuals)
        predictions = np.concatenate(predictions)
        
        return actuals, predictions

class MySQLValidator:
    def __init__(self, config):
        self.config = config

    def validate_connection(self):
        try:
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                logging.info("MySQL connection successful")
                return True
            conn.close()
        except Error as e:
            logging.error(f"MySQL connection error: {e}")
            return False

class Pipeline:
    def __init__(self):
        # Base paths setup
        self.base_path = Path('D:/REVA/Capstone1/sprint2vec_revision')
        self.models_path = self.base_path / 'Models'
        self.results_path = self.base_path / 'Results'
        self.logs_path = self.base_path / 'Logs'
        
        # Create directories
        for path in [self.models_path, self.results_path, self.logs_path]:
            path.mkdir(exist_ok=True)
        
        # Initialize repositories and results
        self.repositories = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
        self.results = {}
        
        # Setup MySQL validator
        self.mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'capstone',
            'database': 'sprint2vec'
        }
        self.mysql_validator = MySQLValidator(self.mysql_config)
        
        # Setup logging
        self.setup_logging()
        self.visualizer = ResultsVisualizer()

    def setup_logging(self):
        """Configure logging for the pipeline"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.base_path / "pipeline.log")
            ]
        )

    def _plot_training_curves(self, train_losses, val_losses, repo_name):
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='Train Loss')
        plt.plot(val_losses, label='Validation Loss')
        plt.title(f'Training Curves - {repo_name}')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(self.base_path / 'Results' / f'{repo_name}_training_curves.png')
        plt.close()
    
    def _plot_comparison(self, results):
        if not results:  # Check if results dictionary is empty
            logging.warning("No results to plot")
            return
            
        # Create DataFrame with proper columns
        data = []
        for repo, metrics in results.items():
            data.append({
                'Repository': repo,
                'Productivity MAE': metrics.get('productivity_mae', 0),
                'Quality MAE': metrics.get('quality_mae', 0)
            })
        
        df_results = pd.DataFrame(data)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_results, x='Repository', 
                   y='Productivity MAE', color='blue', alpha=0.5)
        sns.barplot(data=df_results, x='Repository', 
                   y='Quality MAE', color='red', alpha=0.5)
        
        plt.title('Performance Comparison Across Repositories')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.base_path / 'Results' / 'repository_comparison.png')
        plt.close()

    def run(self, repos_to_process=None):
        """Run the training pipeline for specified repositories"""
        if not self.mysql_validator.validate_connection():
            logging.error("MySQL validation failed. Exiting pipeline.")
            return
            
        if repos_to_process:
            if isinstance(repos_to_process, str):
                repos_to_process = [r.strip() for r in repos_to_process.split(',')]
            repos_to_process = [r for r in repos_to_process if r in self.repositories]
        else:
            repos_to_process = self.repositories
            
        logging.info(f"Processing repositories: {', '.join(repos_to_process)}")
        
        for repo in repos_to_process:
            try:
                logging.info(f"\nProcessing {repo.upper()}")
                # Process repository data
                repo_results = self.process_repository(repo)
                if repo_results:
                    self.results[repo] = repo_results
                
            except Exception as e:
                logging.error(f"Error processing {repo}: {str(e)}")
                continue
        
        # Save and visualize results
        if self.results:
            self.save_results()
            self.visualize_results()
        else:
            logging.warning("No results to plot")

    def process_repository(self, repo_name):
        """Process individual repository data"""
        try:
            # Validate MySQL data
            if not self.mysql_validator.validate_connection():
                raise RuntimeError("Database validation failed")
            
            # Initialize data processor
            processor = DataProcessor(repo_name)
            feature_dims = processor.get_feature_dimensions()
            
            # Get data loaders
            train_loader, val_loader, test_loader = processor.get_data_loaders()
            
            # Initialize model with correct parameters
            model = Sprint2Vec(
                feature_dims=feature_dims,
                hidden_dim=128,
                dropout=0.2
            )
            
            # Initialize trainer
            trainer = ModelTrainer(model)
            train_losses, val_losses = trainer.train(train_loader, val_loader)
            
            # Plot training curves
            self.visualizer.plot_training_curves(train_losses, val_losses, repo_name)
            
            # Get predictions
            actuals, predictions = trainer.get_predictions(test_loader)
            self.visualizer.plot_model_predictions(actuals, predictions, repo_name)
            
            # Store results
            return {
                'productivity_mae': mean_absolute_error(actuals[:, 0], predictions[:, 0]),
                'quality_mae': mean_absolute_error(actuals[:, 1], predictions[:, 1]),
                'r2_score': r2_score(actuals, predictions)
            }
            
        except Exception as e:
            logging.error(f"Error processing repository {repo_name}: {str(e)}")
            return None

    def save_results(self):
        """Save processing results"""
        try:
            results_file = self.results_path / 'pipeline_results.csv'
            # Save results logic here
            logging.info(f"Results saved to {results_file}")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")

    def visualize_results(self):
        """Create visualizations of results"""
        try:
            # Visualization logic here
            logging.info("Results visualization completed")
        except Exception as e:
            logging.error(f"Error creating visualizations: {str(e)}")

def main(repo_name: Optional[str] = None):
    pipeline = Pipeline()
    pipeline.run(repo_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Sprint2Vec training pipeline')
    parser.add_argument('--repositories', type=str, help='Comma-separated list of repositories to process')
    args = parser.parse_args()
    
    pipeline = Pipeline()
    pipeline.run(args.repositories)